import asyncio
import inspect
import threading

from hindsight_client import Hindsight


class MeetingMemory:

    # =========================================================
    # INITIALIZE HINDSIGHT
    # =========================================================

    def __init__(self):

        self.bank_id = "meeting-prep-agent-v2"

        # Create Hindsight client
        self.client = Hindsight(
            base_url="http://localhost:8888"
        )

        # Create memory bank if it does not already exist
        try:

            result = self.client.create_bank(
                bank_id=self.bank_id,
                name="Meeting Prep Agent V2"
            )

            self._resolve(result)

        except Exception:
            # Bank may already exist
            pass


    # =========================================================
    # RESOLVE ASYNC RESULTS
    # =========================================================

    def _resolve(self, value):

        # Normal non-async result
        if not inspect.isawaitable(value):
            return value

        # Check whether an event loop is already running
        try:

            asyncio.get_running_loop()

            loop_is_running = True

        except RuntimeError:

            loop_is_running = False


        # -----------------------------------------------------
        # NO RUNNING LOOP
        # -----------------------------------------------------

        if not loop_is_running:

            return asyncio.run(value)


        # -----------------------------------------------------
        # RUNNING LOOP
        # -----------------------------------------------------

        result = []
        error = []


        def runner():

            try:

                result.append(
                    asyncio.run(value)
                )

            except Exception as e:

                error.append(e)


        thread = threading.Thread(
            target=runner
        )

        thread.start()
        thread.join()


        if error:

            raise error[0]


        if result:

            return result[0]


        return None


    # =========================================================
    # STORE MEETING
    # =========================================================

    def store_meeting(self, meeting):

        meeting_id = meeting.get(
            "meeting_id",
            "unknown"
        )

        date = meeting.get(
            "date",
            "unknown"
        )

        contact = meeting.get(
            "contact",
            "unknown"
        )

        title = meeting.get(
            "title",
            "Untitled Meeting"
        )


        # -----------------------------------------------------
        # DISCUSSION
        # -----------------------------------------------------

        discussions = meeting.get(
            "discussion",
            []
        )

        discussion_text = "\n".join(
            f"- {item}"
            for item in discussions
        )

        if not discussion_text:

            discussion_text = "- None"


        # -----------------------------------------------------
        # DECISIONS
        # -----------------------------------------------------

        decisions = meeting.get(
            "decisions",
            []
        )

        decision_text = "\n".join(
            f"- {item}"
            for item in decisions
        )

        if not decision_text:

            decision_text = "- None"


        # -----------------------------------------------------
        # PROMISES
        # -----------------------------------------------------

        promises = meeting.get(
            "promises",
            []
        )

        promise_lines = []

        for item in promises:

            person = item.get(
                "person",
                "Unknown"
            )

            promise = item.get(
                "promise",
                "Not specified"
            )

            status = item.get(
                "status",
                "Unknown"
            )

            promise_lines.append(
                f"- {person}: "
                f"{promise} "
                f"(Status: {status})"
            )


        promise_text = "\n".join(
            promise_lines
        )

        if not promise_text:

            promise_text = "- None"


        # -----------------------------------------------------
        # FOLLOW-UPS
        # -----------------------------------------------------

        follow_ups = meeting.get(
            "follow_ups",
            []
        )

        followup_lines = []

        for item in follow_ups:

            person = item.get(
                "person",
                "Unknown"
            )

            task = item.get(
                "task",
                "Not specified"
            )

            status = item.get(
                "status",
                "Unknown"
            )

            followup_lines.append(
                f"- {person}: "
                f"{task} "
                f"(Status: {status})"
            )


        followup_text = "\n".join(
            followup_lines
        )

        if not followup_text:

            followup_text = "- None"


        # =====================================================
        # BUILD MEMORY CONTENT
        # =====================================================

        content = f"""
MEETING RECORD

Meeting ID:
{meeting_id}

Date:
{date}

Contact:
{contact}

Meeting Title:
{title}

DISCUSSION:
{discussion_text}

DECISIONS:
{decision_text}

PROMISES / COMMITMENTS:
{promise_text}

FOLLOW-UPS:
{followup_text}

This information represents a previous completed meeting.
Use it as historical context for future meeting preparation.
"""


        # =====================================================
        # STORE IN HINDSIGHT
        # =====================================================

        result = self.client.retain(
            bank_id=self.bank_id,
            content=content,
            document_id=f"meeting-{meeting_id}",
            retain_async=True
        )


        self._resolve(result)


        print(
            f"Meeting {meeting_id} stored in Hindsight."
        )


    # =========================================================
    # RECALL MEMORY
    # =========================================================

    def recall(self, query):

        result = self.client.recall(
            bank_id=self.bank_id,
            query=query
        )


        result = self._resolve(
            result
        )


        if result is None:

            return []


        # -----------------------------------------------------
        # GET RESULTS
        # -----------------------------------------------------

        memories = getattr(
            result,
            "results",
            []
        )


        memories = self._resolve(
            memories
        )


        if memories is None:

            return []


        return list(
            memories
        )