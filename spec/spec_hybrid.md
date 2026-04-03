# Requirement ID: FR_hybrid_1
- Description: The system shall provide a visible chat entry action on the home screen that opens an active support conversation in no more than one tap.
- Source Persona: P_hybrid_1 - Immediate Emotional Support Seeker
- Traceability: Derived from review group H1
- Acceptance Criteria: Given the user is on the home screen, when the user selects the primary support action, then an active chat input opens within 3 seconds and no additional navigation step is required.
- Notes: Refined from the automated support requirement to make the entry behavior observable and measurable.

# Requirement ID: FR_hybrid_2
- Description: The system shall respond to messages expressing stress, loneliness, or overwhelm with a non-judgmental acknowledgment before suggesting any next step.
- Source Persona: P_hybrid_1 - Immediate Emotional Support Seeker
- Traceability: Derived from review group H1
- Acceptance Criteria: Given the user sends a message describing stress, loneliness, or overwhelm, when the system replies, then the first reply acknowledges the emotional state and does not contain blaming, mocking, or dismissive language.
- Notes: Rewritten to preserve the emotional-support goal while improving testability.

# Requirement ID: FR_hybrid_3
- Description: The system shall display separate tool entries for breathing, grounding, journaling, and meditation in the self-help tools area.
- Source Persona: P_hybrid_2 - Structured Coping Tool User
- Traceability: Derived from review group H2
- Acceptance Criteria: Given the user opens the tools area, when the screen finishes loading, then breathing, grounding, journaling, and meditation each appear as separate selectable entries.
- Notes: Revised from the automated tools requirement to align more closely with the grouped review evidence.

# Requirement ID: FR_hybrid_4
- Description: The system shall recommend a coping exercise that matches the user's stated issue instead of repeatedly suggesting the same exercise regardless of context.
- Source Persona: P_hybrid_2 - Structured Coping Tool User
- Traceability: Derived from review group H2
- Acceptance Criteria: Given the user describes a specific issue and requests help, when the system recommends an exercise, then the recommendation references the user's stated issue and is not identical to the immediately previous recommendation unless the user asks to repeat it.
- Notes: Added to address repeated complaints that exercises feel generic or poorly timed.

# Requirement ID: FR_hybrid_5
- Description: The system shall generate replies that reference at least one topic or feeling from the user's immediately preceding message.
- Source Persona: P_hybrid_3 - Context-Sensitive Conversation User
- Traceability: Derived from review group H3
- Acceptance Criteria: Given the user sends a message containing a specific situation or feeling, when the system replies, then the reply includes at least one matching topic, event, or feeling from that message.
- Notes: Preserved the core automated intent but made the response relevance criteria explicit.

# Requirement ID: FR_hybrid_6
- Description: The system shall preserve the active conversation context across at least 10 consecutive user turns within the same session.
- Source Persona: P_hybrid_3 - Context-Sensitive Conversation User
- Traceability: Derived from review group H3
- Acceptance Criteria: Given the user has exchanged up to 10 turns in one session, when the user asks a follow-up question about an earlier topic, then the system continues the same topic without restarting from a generic introduction.
- Notes: Revised to make context retention measurable and directly testable.

# Requirement ID: FR_hybrid_7
- Description: The system shall show the free tier and paid tier in separate labeled sections on the pricing screen before any purchase confirmation step.
- Source Persona: P_hybrid_4 - Price-Sensitive Support User
- Traceability: Derived from review group H4
- Acceptance Criteria: Given the user opens the pricing screen, when the screen finishes loading, then the interface shows one labeled free section and one labeled paid section before any checkout or subscription confirmation step.
- Notes: Tightened the automated pricing requirement by making the labeling and placement expectations explicit.

# Requirement ID: FR_hybrid_8
- Description: The system shall display the current subscription price and billing period on the same screen as the paid feature list.
- Source Persona: P_hybrid_4 - Price-Sensitive Support User
- Traceability: Derived from review group H4
- Acceptance Criteria: Given the user is viewing the pricing screen, when the paid feature list is shown, then the interface also displays the subscription price and billing period without requiring an additional screen.
- Notes: Added to address review complaints about unclear cost expectations.

# Requirement ID: FR_hybrid_9
- Description: The system shall display the chat screen and accept user input within 2 seconds after the user opens an existing conversation under normal network conditions.
- Source Persona: P_hybrid_5 - Reliability-Dependent Distressed User
- Traceability: Derived from review group H5
- Acceptance Criteria: Given the user opens an existing conversation on a supported device with normal network connectivity, when the chat screen is requested, then the message list and text input become interactive within 2 seconds.
- Notes: Rewritten from the automated reliability requirement to focus on a concrete performance target.

# Requirement ID: FR_hybrid_10
- Description: The system shall restore same-day chat history after the app is interrupted and reopened.
- Source Persona: P_hybrid_5 - Reliability-Dependent Distressed User
- Traceability: Derived from review group H5
- Acceptance Criteria: Given the user completed at least one message exchange earlier in the day, when the app is closed, interrupted, or sent to the background and then reopened on the same day, then the previous messages from that conversation are displayed again.
- Notes: Refined from the automated continuity requirement to focus on the specific restoration behavior supported by the review evidence.
