import spacy
import openai
from spacy.matcher import Matcher
# from functions.patterns import blank_pattern


# Load the SpaCy language model
nlp = spacy.load("en_core_web_sm")

# GPT API Key
openai.api_key = "your_api_key"


def detect_fill_in_the_blanks(text):
    try:
        # Process the text with SpaCy
        blank_pattern = [
            {"TEXT": {"REGEX": r"^\d+\."}},
            {"TEXT": {"REGEX": r".*"}}
        ]

        matcher = Matcher(nlp.vocab)
        matcher.add("numbered_sentence", [blank_pattern])

        # Apply the matcher to the text
        doc = nlp(text)
        matches = matcher(doc)
        questions = []
        answers = []
        detected_sentences = []

        # Iterate over sentences using the Matcher
        for match_id, start, end in matcher(doc):
            detected_sentences.append(doc[start:end].text.strip())

        # Print the detected sentences
        for i, sentence in enumerate(detected_sentences, start=1):
            print(f"{i}. {sentence}")
        # for match_id, start, end in matches:
        #     # Find the sentence containing the matching text
        #     sentence = None
        #     for sent in doc.sents:
        #         if start >= sent.start and end <= sent.end:
        #             sentence = sent
        #             break

        #     # Extract the entire sentence
        #     if sentence:
        #         matched_text = sentence.text
        #         questions.append(matched_text)
        #         answers.append("yourself")
            # print(f"Matched: {matched_text} (start: {start}, end: {end})")

        # matcher = Matcher(nlp.vocab)
        # matcher.add("fill_in_the_blanks", [blank_pattern])
        # doc = nlp(text)
        # matches = matcher(doc)
        # for match_id, start, end in matches:
        #     matched_text = doc[start:end].text
        # Initialize variables to track detected questions and their answers

        # Iterate through sentences in the text
        # for sentence in doc.sents:
        #     if any(str(i) + "." in sentence.text for i in range(1, 11)) or "__" in sentence.text:
        #         questions.append(sentence.text)
        #         answers.append("yourself")
        # doc = nlp(sentence)
        # print(sentence)
        # matches = matcher(doc)
        # if matches:
        #     matched_text = doc[matches[0][1]:matches[0][2]].text
        #     print("Matched Text:", matched_text)
        # for match_id, start, end in matcher(doc):
        # matched_text = doc[start:end].text

        # Check if the detected questions are fill-in-the-blanks
        fill_in_the_blanks = [
            {
                "question": '',
                "answer": ''
            }
        ]
        for i, question in enumerate(questions):
            # if "___" in question:
            fill_in_the_blanks.append({
                "question": question,
                "answer": answers[i]
            })

        return fill_in_the_blanks

    except Exception as e:
        return str(e)


def enhance_question_with_gpt(question):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=question,
        max_tokens=3000  # Adjust the token limit as needed
    )
    enhanced_question = response.choices[0].text.strip()
    return enhanced_question
