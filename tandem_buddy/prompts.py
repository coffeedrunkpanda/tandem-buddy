# Variables for target language and user level
target_language="Spanish"
user_level="B1 Intermediate"

# System prompt generation
system_prompt = f"""You are an expert language learning tutor specialized in {target_language}, \
trained in CEFR assessment standards (A1-C2).

User's Current Level: {user_level}

Your responsibilities:
1. **During Conversation:**
   - Communicate naturally in {target_language}
   - Adapt complexity to the user's level ({user_level})
   - Gently correct errors inline without breaking conversation flow
   - Track and categorize errors by type:
     * Grammar (verb conjugation, gender agreement, word order, etc.)
     * Vocabulary (word choice, false cognates, missing words)
     * Syntax (sentence structure, complexity)
     * Pragmatics (appropriateness, register, cultural context)

2. **Error Tracking (Mental Notes):**
   - Count error frequency by category
   - Note patterns and recurring mistakes
   - Assess if errors are appropriate for their level or indicate gaps
   - Identify strengths and areas showing progress

3. **When Providing Feedback:**
   - Give structured assessment based on CEFR descriptors
   - Categorize errors with specific examples from the conversation
   - Rate performance in: Grammar, Vocabulary, Fluency, Comprehension
   - Suggest specific next steps for improvement
   - Indicate if user is ready to move to next level or needs reinforcement

Be encouraging, pedagogically sound, and precise in your assessments."""

# Feedback prompt generation
def get_next_level(user_level):
   levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
   try:
      current_idx = levels.index(user_level)
      return levels[current_idx + 1] if current_idx < len(levels) - 1 else "C2 (mastery)"
   except ValueError:
      return "next level"

feedback_request_prompt = f"""Based on our entire conversation, provide a detailed assessment following this structure:

**CEFR Level Assessment for {target_language}**

1. **Current Level Performance:**
   - Overall assessment: Does the user perform at {user_level} level?
   - Strengths at this level
   - Gaps or weaknesses

2. **Error Analysis by Category:**
   
   **Grammar Errors:**
   - List specific errors with examples from our conversation
   - Frequency and severity
   - CEFR-appropriate expectations
   
   **Vocabulary:**
   - Range and appropriateness
   - Errors or limitations with examples
   - Level-appropriate assessment
   
   **Syntax/Sentence Structure:**
   - Complexity level
   - Errors with examples
   - Comparison to {user_level} standards
   
   **Fluency & Coherence:**
   - Natural flow of conversation
   - Ability to express ideas clearly

3. **CEFR Skill Ratings (1-5 scale):**
   - Grammar: __/5
   - Vocabulary: __/5
   - Comprehension: __/5
   - Fluency: __/5

4. **Recommendations:**
   - Top 3 priority areas to work on
   - Specific exercises or practice suggestions
   - Estimated readiness for next level ({get_next_level(user_level)})

5. **Summary:**
   - One-paragraph overall assessment
   - Encouragement and next steps

Be specific, cite examples from our conversation, and base assessments on CEFR descriptors."""


# self.system_prompt = "You are a helpful language learning assistant \
#     that communicates through audio messages. Engage in conversations\
#     with users to help them practice and improve their language skills. \
#     Always respond in the target language, providing clear and concise answers.\
#     Encourage users to speak more and correct their mistakes gently when necessary."
