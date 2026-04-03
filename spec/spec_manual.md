# Requirement ID: FR1

- Description: The system shall provide a conversation entry point that allows a user to start a support chat from the home screen in no more than one tap.
- Source Persona: P1 - Emotionally Overloaded Support Seeker
- Traceability: Derived from review group G1
- Acceptance Criteria: Given the user is on the home screen, when the user taps the primary support action, then a chat session opens and accepts text input within 3 seconds.

# Requirement ID: FR2

- Description: The system shall display a non-judgmental acknowledgment message after a user submits an emotional disclosure in the chat.
- Source Persona: P1 - Emotionally Overloaded Support Seeker
- Traceability: Derived from review group G1
- Acceptance Criteria: Given the user sends a message describing stress, loneliness, or anxiety, when the system responds, then the first response includes an acknowledgment of the user's emotional state and does not contain blaming or dismissive wording.

# Requirement ID: FR3

- Description: The system shall offer at least three self-help exercise categories: breathing, journaling, and thought reframing.
- Source Persona: P2 - Self-Guided Coping Tool User
- Traceability: Derived from review group G2
- Acceptance Criteria: Given the user opens the self-help tools area, when the screen loads, then the interface shows distinct options for breathing, journaling, and thought reframing exercises.

# Requirement ID: FR4

- Description: The system shall allow a user to start any listed self-help exercise within 2 taps from the tools area.
- Source Persona: P2 - Self-Guided Coping Tool User
- Traceability: Derived from review group G2
- Acceptance Criteria: Given the user is viewing the tools area, when the user selects a listed exercise, then the selected exercise starts within 2 taps and displays its first instruction within 3 seconds.

# Requirement ID: FR5

- Description: The system shall generate chat responses that reference at least one topic or feeling stated in the user's immediately preceding message.
- Source Persona: P3 - Context-Aware Conversation Critic
- Traceability: Derived from review group G3
- Acceptance Criteria: Given the user sends a message containing a specific concern, when the system replies, then the reply includes at least one matching topic, feeling, or situation from that message.

# Requirement ID: FR6

- Description: The system shall preserve the last 20 turns of the active chat session so that the conversation can continue with context.
- Source Persona: P3 - Context-Aware Conversation Critic
- Traceability: Derived from review group G3
- Acceptance Criteria: Given the user has exchanged 20 or fewer turns in a session, when the user sends a follow-up message, then the system can reference details from earlier turns in the same session without restarting the conversation.

# Requirement ID: FR7

- Description: The system shall present free features and paid features in separate labeled sections before asking the user to upgrade.
- Source Persona: P4 - Price-Conscious Mental Health User
- Traceability: Derived from review group G4
- Acceptance Criteria: Given a user opens the pricing or upgrade screen, when the screen is displayed, then it shows one labeled section for free features and one labeled section for paid features before any purchase confirmation step.

# Requirement ID: FR8

- Description: The system shall allow a user to dismiss an upgrade prompt and continue using the free conversation flow if the current feature is part of the free tier.
- Source Persona: P4 - Price-Conscious Mental Health User
- Traceability: Derived from review group G4
- Acceptance Criteria: Given a user is using a free-tier feature and an upgrade prompt appears, when the user selects the dismiss action, then the user returns to the same free-tier flow without losing progress.

# Requirement ID: FR9

- Description: The system shall load the home screen and the active chat screen within 3 seconds under normal network conditions.
- Source Persona: P5 - Reliability-Focused User in Distress
- Traceability: Derived from review group G5
- Acceptance Criteria: Given the app is launched on a supported device with normal network connectivity, when the home screen or an existing chat screen is opened, then the requested screen becomes interactive within 3 seconds.

# Requirement ID: FR10

- Description: The system shall preserve unsent draft text and completed chat history when the app is temporarily interrupted and reopened within the same day.
- Source Persona: P5 - Reliability-Focused User in Distress
- Traceability: Derived from review group G5
- Acceptance Criteria: Given the user has typed a draft or completed a chat exchange, when the app is closed unexpectedly or sent to the background and reopened on the same day, then the draft text and prior chat messages are restored.
