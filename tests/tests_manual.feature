Feature: Manual validation scenarios for the Wysa support app

  Scenario: FR1 Open support chat from the home screen
    Given the user is on the home screen
    When the user taps the primary support action
    Then a chat session opens and accepts text input within 3 seconds

  Scenario: FR1 Reach chat in no more than one tap
    Given the user is on the home screen
    When the user navigates to the support chat
    Then the chat is reachable in no more than one tap

  Scenario: FR2 Acknowledge stressful disclosure
    Given the user is in an active support chat
    When the user sends a message about feeling overwhelmed and anxious
    Then the first response acknowledges the emotional state without blaming or dismissive wording

  Scenario: FR2 Acknowledge loneliness disclosure
    Given the user is in an active support chat
    When the user sends a message about feeling alone and needing someone to talk to
    Then the first response references loneliness or support and remains non-judgmental

  Scenario: FR3 Show breathing journaling and thought reframing categories
    Given the user opens the self-help tools area
    When the tools area finishes loading
    Then breathing journaling and thought reframing are shown as distinct categories

  Scenario: FR3 Keep categories visible after reopening the tools area
    Given the user has opened the self-help tools area once
    When the user reopens the tools area
    Then breathing journaling and thought reframing remain available as separate categories

  Scenario: FR4 Start a breathing exercise quickly
    Given the user is in the self-help tools area
    When the user selects a breathing exercise
    Then the exercise starts within 2 taps and shows the first instruction within 3 seconds

  Scenario: FR4 Start a journaling exercise quickly
    Given the user is in the self-help tools area
    When the user selects a journaling exercise
    Then the exercise starts within 2 taps and shows the first prompt within 3 seconds

  Scenario: FR5 Reference the user's immediate concern
    Given the user is in an active support chat
    When the user says they are nervous about tomorrow's exam and cannot sleep
    Then the reply references the exam the nervousness or the sleep difficulty

  Scenario: FR5 Reference the user's social situation
    Given the user is in an active support chat
    When the user says they argued with a friend and feel guilty
    Then the reply references the friendship conflict or the guilt

  Scenario: FR6 Maintain context across multiple turns
    Given the user has exchanged several turns about work stress in one session
    When the user asks a follow-up question about the same stressor
    Then the response reflects details from the earlier turns

  Scenario: FR6 Do not restart the conversation after a follow-up
    Given the user has already described a specific concern in the current session
    When the user sends a follow-up message
    Then the system continues the same conversation instead of resetting to a generic introduction

  Scenario: FR7 Label free and paid sections
    Given the user opens the pricing or upgrade screen
    When the screen is displayed
    Then one labeled free section and one labeled paid section are visible before checkout

  Scenario: FR7 Show pricing structure before purchase confirmation
    Given the user is reviewing the pricing or upgrade screen
    When the user has not yet chosen to purchase
    Then the free and paid feature sets are already separated and labeled

  Scenario: FR8 Dismiss an upgrade prompt in a free-tier flow
    Given the user is using a free-tier feature
    When an upgrade prompt appears and the user dismisses it
    Then the user returns to the same free-tier flow without losing progress

  Scenario: FR8 Preserve entered text after dismissing upgrade
    Given the user has entered text in a free-tier conversation flow
    When an upgrade prompt appears and the user dismisses it
    Then the previously entered text remains available

  Scenario: FR9 Load the home screen within the target time
    Given the app is launched on a supported device with normal network connectivity
    When the home screen is requested
    Then the home screen becomes interactive within 3 seconds

  Scenario: FR9 Load the active chat screen within the target time
    Given an existing chat session is opened on a supported device with normal network connectivity
    When the chat screen is requested
    Then the chat screen becomes interactive within 3 seconds

  Scenario: FR10 Restore unsent draft text after interruption
    Given the user has typed a draft message without sending it
    When the app is interrupted and reopened on the same day
    Then the unsent draft text is restored

  Scenario: FR10 Restore chat history after interruption
    Given the user completed a multi-turn chat conversation
    When the app is interrupted and reopened on the same day
    Then the previous chat messages are restored
