from memory import MeetingMemory
import ollama


class MeetingPrepAgent:

    def __init__(self):

        self.memory = MeetingMemory()

        self.meetings = []


    # =========================================================
    # ADD MEETING
    # =========================================================

    def add_meeting(self, meeting):

        self.meetings.append(
            meeting
        )

        self.memory.store_meeting(
            meeting
        )

        print(
            f"Meeting {meeting.get('meeting_id', 'unknown')} "
            "stored successfully."
        )


    # =========================================================
    # PREPARE MEETING
    # =========================================================

    def prepare_meeting(
        self,
        contact,
        agenda
    ):

        print(
            "\nSearching previous interactions..."
        )


        # -----------------------------------------------------
        # CONTACT-SPECIFIC HINDSIGHT SEARCH
        # -----------------------------------------------------

        query = f"""
Find previous interactions and relevant context
with the following contact.

CONTACT:
{contact}

UPCOMING MEETING AGENDA:
{agenda}

Focus on:

- previous discussions with this contact
- previous decisions involving this contact
- promises made by this contact
- pending commitments
- missed follow-ups
- completed work
- unresolved issues
- important project context
- previous topics related to the upcoming agenda

Return only information supported by previous meetings.

Do not invent information.
"""


        memories = self.memory.recall(
            query
        )


        # =====================================================
        # EXACT FACTS FROM STORED MEETINGS
        # =====================================================

        decisions = []

        pending_promises = []

        missed_followups = []

        completed_items = []

        discussions = []


        # -----------------------------------------------------
        # FILTER BY CONTACT
        # -----------------------------------------------------

        contact_lower = contact.strip().lower()


        for meeting in self.meetings:

            meeting_contact = str(
                meeting.get(
                    "contact",
                    ""
                )
            ).strip().lower()


            # Only use meetings involving the requested contact
            if meeting_contact != contact_lower:

                continue


            # -------------------------------------------------
            # DECISIONS
            # -------------------------------------------------

            for decision in meeting.get(
                "decisions",
                []
            ):

                if decision not in decisions:

                    decisions.append(
                        decision
                    )


            # -------------------------------------------------
            # DISCUSSIONS
            # -------------------------------------------------

            for discussion in meeting.get(
                "discussion",
                []
            ):

                if discussion not in discussions:

                    discussions.append(
                        discussion
                    )


            # -------------------------------------------------
            # PROMISES
            # -------------------------------------------------

            for item in meeting.get(
                "promises",
                []
            ):

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


                status_lower = (
                    status.lower()
                )


                entry = (
                    f"{person} | "
                    f"{promise} | "
                    f"Status: {status}"
                )


                if status_lower in [
                    "pending",
                    "still pending"
                ]:

                    if entry not in pending_promises:

                        pending_promises.append(
                            entry
                        )


                elif status_lower == "completed":

                    if entry not in completed_items:

                        completed_items.append(
                            entry
                        )


            # -------------------------------------------------
            # FOLLOW-UPS
            # -------------------------------------------------

            for item in meeting.get(
                "follow_ups",
                []
            ):

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


                status_lower = (
                    status.lower()
                )


                entry = (
                    f"{person} | "
                    f"{task} | "
                    f"Status: {status}"
                )


                if status_lower == "missed":

                    if entry not in missed_followups:

                        missed_followups.append(
                            entry
                        )


                elif status_lower == "completed":

                    if entry not in completed_items:

                        completed_items.append(
                            entry
                        )


        # =====================================================
        # CONVERT FACTS TO TEXT
        # =====================================================

        decisions_text = (

            "\n".join(
                f"- {item}"
                for item in decisions
            )

            if decisions

            else "- None"
        )


        pending_text = (

            "\n".join(
                f"- {item}"
                for item in pending_promises
            )

            if pending_promises

            else "- None"
        )


        missed_text = (

            "\n".join(
                f"- {item}"
                for item in missed_followups
            )

            if missed_followups

            else "- None"
        )


        completed_text = (

            "\n".join(
                f"- {item}"
                for item in completed_items
            )

            if completed_items

            else "- None"
        )


        discussions_text = (

            "\n".join(
                f"- {item}"
                for item in discussions
            )

            if discussions

            else "- None"
        )


        # =====================================================
        # EXACT FACTS
        # =====================================================

        exact_facts = f"""

CONTACT:
{contact}

PREVIOUS DECISIONS:
{decisions_text}

PENDING PROMISES:
{pending_text}

MISSED FOLLOW-UPS:
{missed_text}

COMPLETED ITEMS:
{completed_text}

KEY DISCUSSIONS:
{discussions_text}
"""


        # =====================================================
        # HINDSIGHT CONTEXT
        # =====================================================

        hindsight_context = ""

        seen = set()


        for memory in memories:

            text = memory.text.strip()


            if text and text not in seen:

                seen.add(
                    text
                )

                hindsight_context += (
                    f"- {text}\n"
                )


        if not hindsight_context:

            hindsight_context = (
                "No additional Hindsight memory available."
            )


        # =====================================================
        # AI PROMPT
        # =====================================================

        prompt = f"""
You are a strict professional Meeting Preparation Agent.

Your job is to prepare a meeting brief using the
past interactions with one specific contact.

CONTACT:
{contact}

UPCOMING MEETING AGENDA:
{agenda}

EXACT FACTS FROM PREVIOUS INTERACTIONS:
{exact_facts}

RELEVANT HINDSIGHT MEMORY:
{hindsight_context}


IMPORTANT ACCURACY RULES:

1. The EXACT FACTS section is authoritative.

2. Use only information explicitly provided.

3. Never invent information.

4. Never invent deadlines.

5. Never invent dates.

6. Never invent names.

7. Never invent tasks.

8. Never invent promises.

9. Never invent decisions.

10. Never invent progress.

11. Never assume a deadline.

12. Never assume that a pending task is completed.

13. Preserve the original status exactly.

14. "Pending" means Pending.

15. "Still Pending" means Still Pending.

16. "Completed" means Completed.

17. "Missed" means Missed.

18. Do not claim something is completed unless
the source explicitly says it is completed.

19. Do not create new facts by combining unrelated facts.

20. Do not repeat identical information.

21. Do not add dates unless explicitly present.

22. Do not add a completion date unless explicitly present.

23. Do not suggest a revised deadline unless the source
explicitly provides one.

24. Keep the brief focused on the selected contact.

25. If information is unavailable, write:
"Not available from previous meetings."

26. Do not treat Hindsight-generated information as
more authoritative than the EXACT FACTS section.

27. Use Hindsight memory only when it is relevant
to the selected contact and agenda.


CREATE EXACTLY THESE SECTIONS:

1. CONTACT CONTEXT
2. PREVIOUS DECISIONS
3. PENDING PROMISES
4. MISSED FOLLOW-UPS
5. COMPLETED ITEMS
6. UNRESOLVED ISSUES
7. KEY DISCUSSION POINTS
8. QUESTIONS TO ASK
9. SUGGESTED FOLLOW-UP


For sections 1-5:

Use only the exact facts supplied.

For sections 6-9:

Use exact facts and relevant Hindsight memory,
but do not introduce unsupported information.

Return ONLY the meeting preparation brief.
"""


        # =====================================================
        # GENERATE AI BRIEF
        # =====================================================

        print(
            "\nGenerating meeting brief..."
        )


        response = ollama.chat(

            model="llama3.2",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            options={
                "temperature": 0
            }
        )


        result = (
            response["message"]["content"]
        )


        # =====================================================
        # TERMINAL OUTPUT
        # =====================================================

        print("\n")

        print(
            "=" * 70
        )

        print(
            "              MEETING PREPARATION BRIEF"
        )

        print(
            "=" * 70
        )


        print("\nCONTACT")

        print(
            "-" * 70
        )

        print(
            contact
        )


        print("\nAGENDA")

        print(
            "-" * 70
        )

        print(
            agenda
        )


        print("\nAI-GENERATED PREPARATION")

        print(
            "-" * 70
        )

        print(
            result
        )


        print("\n")

        print(
            "=" * 70
        )

        print(
            "                    END OF BRIEF"
        )

        print(
            "=" * 70
        )


        return result