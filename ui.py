import streamlit as st
import json
import threading
import queue
import time
from datetime import date


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Meeting Prep Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #f7f8fc;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #202533;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 17px;
        color: #6b7280;
        margin-bottom: 30px;
    }

    .info-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #e6e8ef;
        box-shadow: 0 4px 15px rgba(20, 30, 60, 0.05);
        min-height: 120px;
    }

    .card-title {
        font-size: 15px;
        color: #6b7280;
        margin-bottom: 8px;
    }

    .card-value {
        font-size: 19px;
        font-weight: 700;
        color: #202533;
    }

    .card-small {
        font-size: 13px;
        color: #8a91a3;
        margin-top: 6px;
    }

    .section-title {
        font-size: 25px;
        font-weight: 750;
        color: #202533;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    .status-online {
        color: #16803c;
        font-weight: 700;
    }

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e7e9ef;
    }

    textarea {
        border-radius: 12px !important;
    }

    .stButton > button {
        border-radius: 12px;
        height: 52px;
        font-size: 17px;
        font-weight: 700;
    }

    div[data-testid="stProgressBar"] {
        height: 10px;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# LOAD MEETINGS
# =========================================================

def load_meetings():

    with open(
        "data/meetings.json",
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# =========================================================
# SAVE MEETINGS
# =========================================================

def save_meetings(meetings):

    with open(
        "data/meetings.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            meetings,
            file,
            indent=2,
            ensure_ascii=False
        )


# =========================================================
# GET ALL CONTACTS
# =========================================================

def get_contacts(meetings):

    contacts = set()

    for meeting in meetings:

        # Main contact
        contact = meeting.get("contact")

        if contact:
            contacts.add(contact)

        # Participants
        for person in meeting.get(
            "participants",
            []
        ):

            if person:
                contacts.add(person)

        # Promises
        for item in meeting.get(
            "promises",
            []
        ):

            person = item.get("person")

            if person:
                contacts.add(person)

        # Follow-ups
        for item in meeting.get(
            "follow_ups",
            []
        ):

            person = item.get("person")

            if person:
                contacts.add(person)

    return sorted(
        contacts,
        key=lambda x: x.lower()
    )


# =========================================================
# PREPARE MEETING WORKER
# =========================================================

def prepare_meeting_worker(
    meetings,
    contact,
    agenda,
    message_queue,
    result_holder
):

    try:

        # -------------------------------------------------
        # STEP 1
        # -------------------------------------------------

        message_queue.put(
            (
                "step",
                1,
                "Starting Meeting Prep Agent..."
            )
        )

        from meeting_agent import MeetingPrepAgent

        agent = MeetingPrepAgent()

        # -------------------------------------------------
        # STEP 2
        # -------------------------------------------------

        message_queue.put(
            (
                "step",
                2,
                "Connecting to Hindsight memory..."
            )
        )

        time.sleep(0.3)

        # -------------------------------------------------
        # STORE MEETINGS
        # -------------------------------------------------

        total = len(meetings)

        for index, meeting in enumerate(meetings):

            message_queue.put(
                (
                    "meeting",
                    index + 1,
                    total,
                    f"Remembering Meeting "
                    f"{meeting.get('meeting_id', 'Unknown')}..."
                )
            )

            agent.add_meeting(
                meeting
            )

        # -------------------------------------------------
        # STEP 3
        # -------------------------------------------------

        message_queue.put(
            (
                "step",
                3,
                f"Searching previous interactions with {contact}..."
            )
        )

        # -------------------------------------------------
        # STEP 4
        # -------------------------------------------------

        message_queue.put(
            (
                "step",
                4,
                "Llama 3.2 is preparing your meeting brief..."
            )
        )

        # -------------------------------------------------
        # PREPARE BRIEF
        # -------------------------------------------------

        result = agent.prepare_meeting(
            contact,
            agenda
        )

        # -------------------------------------------------
        # COMPLETE
        # -------------------------------------------------

        result_holder["result"] = result

        message_queue.put(
            (
                "done",
                "Meeting preparation completed."
            )
        )

    except Exception as e:

        result_holder["error"] = e

        message_queue.put(
            (
                "error",
                str(e)
            )
        )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🤖 Meeting Prep Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Prepare smarter meetings using the full context of '
    'your past interactions.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# LOAD MEETING DATA
# =========================================================

try:

    meetings = load_meetings()

except Exception as e:

    st.error(
        "Could not load meetings.json"
    )

    st.exception(e)

    st.stop()


# =========================================================
# CONTACT LIST
# =========================================================

contacts = get_contacts(
    meetings
)


# =========================================================
# TOP INFORMATION CARDS
# =========================================================

col1, col2, col3 = st.columns(3)


with col1:

    st.markdown(
        """
        <div class="info-card">

        <div class="card-title">
        🧠 MEMORY
        </div>

        <div class="card-value">
        Hindsight
        </div>

        <div class="card-small">
        Persistent interaction memory
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        """
        <div class="info-card">

        <div class="card-title">
        🤖 AI MODEL
        </div>

        <div class="card-value">
        Llama 3.2
        </div>

        <div class="card-small">
        Running locally with Ollama
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        """
        <div class="info-card">

        <div class="card-title">
        ⚡ SYSTEM
        </div>

        <div class="card-value">
        <span class="status-online">
        ● Online
        </span>
        </div>

        <div class="card-small">
        Meeting preparation ready
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        "## 🧠 Meeting Memory"
    )

    st.success(
        "Hindsight Memory Active"
    )

    st.write(
        "The agent remembers previous interactions "
        "and uses them to prepare for upcoming meetings."
    )

    st.divider()

    st.markdown(
        "### System"
    )

    st.write(
        "🧠 **Memory:** Hindsight"
    )

    st.write(
        "🤖 **LLM:** Llama 3.2"
    )

    st.write(
        "⚡ **Runtime:** Ollama"
    )

    st.write(
        "🐍 **Backend:** Python"
    )

    st.divider()

    st.markdown(
        "### Contacts"
    )

    st.write(
        f"👥 {len(contacts)} people found"
    )

    st.divider()

    st.caption(
        "Meeting Prep Agent • Local AI"
    )


# =========================================================
# UPCOMING MEETING
# =========================================================

st.markdown(
    '<div class="section-title">'
    '📅 Upcoming Meeting'
    '</div>',
    unsafe_allow_html=True
)

st.write(
    "Select the contact and enter the agenda "
    "for your upcoming meeting."
)


# =========================================================
# CONTACT SELECTOR
# =========================================================

contact = st.selectbox(
    "Contact",
    contacts,
    index=0 if contacts else None,
    placeholder="Select a contact"
)


# =========================================================
# AGENDA
# =========================================================

agenda = st.text_area(
    "Meeting agenda",
    placeholder=(
        "Enter your upcoming meeting agenda...\n\n"
        "Examples:\n"
        "• Project progress review\n"
        "• Login API and final testing\n"
        "• Database discussion\n"
        "• Pending tasks\n"
        "• Project status and testing"
    ),
    height=140
)


# =========================================================
# PREPARE BUTTON
# =========================================================

prepare_clicked = st.button(
    "🚀  Prepare Meeting",
    type="primary",
    use_container_width=True
)


# =========================================================
# PREPARE MEETING
# =========================================================

if prepare_clicked:

    if not contact:

        st.warning(
            "Please select a contact."
        )

    elif not agenda.strip():

        st.warning(
            "Please enter a meeting agenda."
        )

    else:

        try:

            # -------------------------------------------------
            # CREATE UI ELEMENTS
            # -------------------------------------------------

            st.divider()

            st.markdown(
                '<div class="section-title">'
                '🧠 Preparing Your Meeting'
                '</div>',
                unsafe_allow_html=True
            )

            progress_bar = st.progress(
                0
            )

            current_status = st.empty()

            # -------------------------------------------------
            # QUEUE
            # -------------------------------------------------

            message_queue = queue.Queue()

            result_holder = {}

            # -------------------------------------------------
            # START WORKER
            # -------------------------------------------------

            thread = threading.Thread(
                target=prepare_meeting_worker,
                args=(
                    meetings,
                    contact,
                    agenda,
                    message_queue,
                    result_holder
                )
            )

            thread.start()

            # -------------------------------------------------
            # LIVE PROGRESS
            # -------------------------------------------------

            while thread.is_alive():

                try:

                    while True:

                        message = (
                            message_queue.get_nowait()
                        )

                        # -------------------------------------
                        # STEP
                        # -------------------------------------

                        if message[0] == "step":

                            step_number = message[1]

                            text = message[2]

                            progress = (
                                step_number / 4
                            )

                            progress_bar.progress(
                                progress
                            )

                            current_status.markdown(
                                f"### 🔄 {text}"
                            )

                        # -------------------------------------
                        # MEETING
                        # -------------------------------------

                        elif message[0] == "meeting":

                            meeting_number = message[1]

                            total = message[2]

                            text = message[3]

                            progress = (
                                0.25
                                +
                                (
                                    meeting_number
                                    /
                                    total
                                )
                                * 0.25
                            )

                            progress_bar.progress(
                                min(
                                    progress,
                                    0.50
                                )
                            )

                            current_status.markdown(
                                f"### 🧠 {text}"
                            )

                        # -------------------------------------
                        # ERROR
                        # -------------------------------------

                        elif message[0] == "error":

                            current_status.error(
                                message[1]
                            )

                except queue.Empty:

                    pass

                time.sleep(
                    0.15
                )

            # -------------------------------------------------
            # FINAL MESSAGES
            # -------------------------------------------------

            while not message_queue.empty():

                message = (
                    message_queue.get()
                )

                if message[0] == "step":

                    step_number = message[1]

                    text = message[2]

                    progress_bar.progress(
                        min(
                            step_number / 4,
                            1.0
                        )
                    )

                    current_status.markdown(
                        f"### 🔄 {text}"
                    )

                elif message[0] == "done":

                    progress_bar.progress(
                        1.0
                    )

                    current_status.success(
                        "✅ Meeting preparation completed!"
                    )

            # -------------------------------------------------
            # ERROR
            # -------------------------------------------------

            if "error" in result_holder:

                st.error(
                    "Something went wrong."
                )

                st.exception(
                    result_holder["error"]
                )

            # -------------------------------------------------
            # RESULT
            # -------------------------------------------------

            elif "result" in result_holder:

                st.session_state.result = (
                    result_holder["result"]
                )

                st.session_state.contact = (
                    contact
                )

                st.session_state.agenda = (
                    agenda
                )

        except Exception as e:

            st.error(
                "Unable to prepare the meeting."
            )

            st.exception(
                e
            )


# =========================================================
# MEETING PREPARATION RESULT
# =========================================================

if "result" in st.session_state:

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '📋 Meeting Preparation Brief'
        '</div>',
        unsafe_allow_html=True
    )

    # -------------------------------------------------------
    # CONTACT
    # -------------------------------------------------------

    if "contact" in st.session_state:

        st.info(
            f"👤 **Contact:** "
            f"{st.session_state.contact}"
        )

    # -------------------------------------------------------
    # AGENDA
    # -------------------------------------------------------

    if "agenda" in st.session_state:

        st.info(
            f"📅 **Upcoming agenda:** "
            f"{st.session_state.agenda}"
        )

    # -------------------------------------------------------
    # RESULT
    # -------------------------------------------------------

    with st.container(
        border=True
    ):

        st.markdown(
            st.session_state.result
        )

    # -------------------------------------------------------
    # FOOTER
    # -------------------------------------------------------

    st.divider()

    st.caption(
        "🤖 Generated using Hindsight Memory + "
        "Llama 3.2 + Ollama"
    )


# =========================================================
# RECORD COMPLETED MEETING
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">'
    '📝 Record Completed Meeting'
    '</div>',
    unsafe_allow_html=True
)

st.write(
    "After the actual meeting, record what happened. "
    "This information can be used for future meeting preparation."
)


# =========================================================
# RECORD MEETING FORM
# =========================================================

record_col1, record_col2 = st.columns(2)


with record_col1:

    record_contact = st.selectbox(
        "Contact",
        contacts,
        index=0 if contacts else None,
        key="record_contact",
        placeholder="Select a contact"
    )


with record_col2:

    meeting_date = st.date_input(
        "Meeting date",
        value=date.today(),
        key="meeting_date"
    )


record_title = st.text_input(
    "Meeting title",
    placeholder="Example: Project Progress Review",
    key="record_title"
)


record_discussion = st.text_area(
    "Discussion",
    placeholder=(
        "What was discussed in the meeting?\n"
        "Example: Login API progress, testing status, database progress"
    ),
    height=120,
    key="record_discussion"
)


record_decisions = st.text_area(
    "Decisions",
    placeholder=(
        "What decisions were made?\n"
        "Example: Start final testing after login API completion"
    ),
    height=120,
    key="record_decisions"
)


record_promises = st.text_area(
    "Promises / Commitments",
    placeholder=(
        "What promises or commitments were made?\n"
        "Example: Rahul will complete the login API"
    ),
    height=120,
    key="record_promises"
)


record_followups = st.text_area(
    "Follow-ups",
    placeholder=(
        "What needs to be followed up?\n"
        "Example: Check login API before final testing"
    ),
    height=120,
    key="record_followups"
)


# =========================================================
# SAVE COMPLETED MEETING BUTTON
# =========================================================

save_meeting_clicked = st.button(
    "💾  Save Completed Meeting",
    type="secondary",
    use_container_width=True
)


# =========================================================
# SAVE COMPLETED MEETING
# =========================================================

if save_meeting_clicked:

    if not record_contact:

        st.warning(
            "Please select a contact."
        )

    elif not record_title.strip():

        st.warning(
            "Please enter a meeting title."
        )

    elif not record_discussion.strip():

        st.warning(
            "Please enter the meeting discussion."
        )

    else:

        try:

            # -------------------------------------------------
            # GET LATEST MEETING ID
            # -------------------------------------------------

            existing_ids = []

            for meeting in meetings:

                meeting_id = meeting.get(
                    "meeting_id"
                )

                if isinstance(
                    meeting_id,
                    int
                ):

                    existing_ids.append(
                        meeting_id
                    )

            if existing_ids:

                new_meeting_id = (
                    max(existing_ids) + 1
                )

            else:

                new_meeting_id = 1


            # -------------------------------------------------
            # CONVERT TEXT TO LISTS
            # -------------------------------------------------

            discussion_list = [
                line.strip()
                for line in record_discussion.splitlines()
                if line.strip()
            ]

            decisions_list = [
                line.strip()
                for line in record_decisions.splitlines()
                if line.strip()
            ]

            # -------------------------------------------------
            # PROMISES
            # -------------------------------------------------

            promises_list = []

            for line in record_promises.splitlines():

                line = line.strip()

                if line:

                    promises_list.append(
                        {
                            "person": record_contact,
                            "promise": line,
                            "status": "Pending"
                        }
                    )

            # -------------------------------------------------
            # FOLLOW-UPS
            # -------------------------------------------------

            followups_list = []

            for line in record_followups.splitlines():

                line = line.strip()

                if line:

                    followups_list.append(
                        {
                            "person": record_contact,
                            "task": line,
                            "status": "Pending"
                        }
                    )

            # -------------------------------------------------
            # CREATE NEW MEETING
            # -------------------------------------------------

            new_meeting = {

                "meeting_id": new_meeting_id,

                "date": meeting_date.isoformat(),

                "contact": record_contact,

                "title": record_title.strip(),

                "participants": [
                    record_contact
                ],

                "discussion": discussion_list,

                "decisions": decisions_list,

                "promises": promises_list,

                "follow_ups": followups_list
            }


            # -------------------------------------------------
            # SAVE TO JSON
            # -------------------------------------------------

            meetings.append(
                new_meeting
            )

            save_meetings(
                meetings
            )


            # -------------------------------------------------
            # STORE IN HINDSIGHT
            # -------------------------------------------------

            from meeting_agent import MeetingPrepAgent

            memory_agent = MeetingPrepAgent()

            memory_agent.add_meeting(
                new_meeting
            )


            # -------------------------------------------------
            # SUCCESS
            # -------------------------------------------------

            st.success(
                f"✅ Meeting {new_meeting_id} saved successfully!"
            )

            st.info(
                "🧠 The completed meeting was saved to "
                "meetings.json and added to Hindsight memory."
            )

            # -------------------------------------------------
            # SHOW SAVED DATA
            # -------------------------------------------------

            with st.expander(
                "View saved meeting"
            ):

                st.json(
                    new_meeting
                )

            # -------------------------------------------------
            # REFRESH CONTACT LIST
            # -------------------------------------------------

            st.session_state["meeting_saved"] = True

        except Exception as e:

            st.error(
                "Unable to save the completed meeting."
            )

            st.exception(
                e
            )


# =========================================================
# FINAL FOOTER
# =========================================================

st.divider()

st.caption(
    "🤖 Meeting Prep Agent • "
    "Hindsight Memory + Llama 3.2 + Ollama"
)