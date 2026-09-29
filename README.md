# 🤖 Meeting Prep Agent

An AI-powered Meeting Preparation Agent that uses **persistent memory** to understand previous interactions and prepare you for upcoming meetings.

The agent combines **Hindsight Memory**, **Llama 3.2**, **Ollama**, and **Streamlit** to retrieve relevant information from previous meetings and generate a concise preparation brief.

---

## 🎯 Problem Statement

Important information from previous meetings is often forgotten or scattered across different conversations.

Before a new meeting, people may need to remember:

- Previous discussions
- Decisions that were made
- Pending promises
- Missed follow-ups
- Completed work
- Unresolved issues
- People responsible for tasks
- Important context from previous interactions

The Meeting Prep Agent solves this problem by maintaining persistent memory of previous interactions and using that information to prepare for an upcoming meeting.

> **An agent that briefs you with full context from every past interaction with a contact is a professional superpower.**

---

# 💡 Solution

The Meeting Prep Agent allows the user to select a contact and enter an upcoming meeting agenda.

The agent then:

1. Loads previous meeting information.
2. Stores previous interactions in Hindsight.
3. Retrieves relevant historical context.
4. Identifies decisions, promises, follow-ups, completed work, and unresolved issues.
5. Uses Llama 3.2 to generate a meeting preparation brief.
6. Displays the result through a Streamlit interface.

---

# 🧠 How It Works

```text
                User
                  │
                  ▼
       ┌─────────────────────┐
       │ Contact + Agenda    │
       └──────────┬──────────┘
                  │
                  ▼
       ┌─────────────────────┐
       │ Meeting Prep Agent  │
       └──────────┬──────────┘
                  │
                  ▼
       ┌─────────────────────┐
       │ Hindsight Memory    │
       │                     │
       │ Previous Meetings   │
       │ Decisions           │
       │ Promises            │
       │ Follow-ups          │
       │ Discussions         │
       └──────────┬──────────┘
                  │
                  ▼
       ┌─────────────────────┐
       │ Relevant Context    │
       └──────────┬──────────┘
                  │
                  ▼
       ┌─────────────────────┐
       │ Llama 3.2           │
       │ via Ollama          │
       └──────────┬──────────┘
                  │
                  ▼
       ┌─────────────────────┐
       │ Meeting Preparation │
       │ Brief               │
       └─────────────────────┘