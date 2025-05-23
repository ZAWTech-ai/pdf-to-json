user_prompt_post_fix = r'''

**Instructions:** 

For "English," generate questions in English. For "Chinese," generate questions in Traditional Chinese following Hong Kong style (not Mainland Chinese style). 

Include time-sensitive words (e.g., "yesterday," "now," "tomorrow") in the question to clearly indicate the required tense. 

- Avoid ambiguous questions by ensuring each question has a single, clear correct answer based on the given context and time-sensitive words. 
- Strictly adhere to the specified grammar topic and tense requirements. For example, if the topic is passive voice in past tense, only generate questions in the past tense passive voice (e.g., "was/were + past participle") and do not include any other tenses (e.g., present or future). If the topic requires present continuous passive voice for ongoing actions (e.g., with "now"), use "is/are being + past participle" exclusively for those contexts. 
- If a question includes a verb in brackets that matches the correct answer, do not include the bracketed verb in the question.

Adjust question complexity based on LEVEL: 
- For K1-K3: Use very simple questions with basic concepts (e.g., single words, short phrases). 
- For P1-P3: Use simple sentences or short passages with basic vocabulary. 
- For P4-P6: Use moderately challenging sentences or short passages with age-appropriate vocabulary. 
- For S1 and above: Use complex sentences or cloze passages with advanced vocabulary. 

Ensure all questions are engaging and appropriate for young learners, avoiding sensitive or inappropriate content. 
For English grammar topics, ensure variety across different grammar concepts (e.g., tenses, passive voice, prepositions, etc.) unless a specific topic is specified. 

Return the response in JSON format with the following structure for each question: 
question: The question text (do not include the answer in this field). 
direction: Clear instructions for the student. 
options: A list of options (for multiple-choice questions only). 
answer: The correct answer(s), supporting multiple answers if applicable (e.g., "don't" and "do not"). 
'''
