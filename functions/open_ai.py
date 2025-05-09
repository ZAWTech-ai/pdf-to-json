from flask import jsonify
from openai import OpenAI
import json
client = OpenAI()


def get_open_ai_completion(prompt: str, model: str = "gpt-4", system_prompt: str = None) -> str:
    """
    Get response from the specified model using the given prompt.

    Args:
        prompt (str): The input prompt to send to the model
        model (str): The model to use for completion (default: "gpt-4")
        system_prompt (str, optional): System prompt to guide the model's behavior

    Returns:
        str: The model's response in JSON format
    """
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Generate appropriate questions and answers of various types (Fill in the blanks, MCQs, Comprehension) tailored to the given subject, topic, and level. Ensure the questions provide meaningful direction and clarity before presenting them in JSON format.\n\n# Steps\n\n1. **Identify Subject, Topic, and Level**: Understand the requirements specified for the subject, topic, and level of difficulty to tailor the questions accordingly.\n2. **Select Appropriate Question Type**: Choose from Fill in the blanks, Multiple Choice Questions (MCQs), or Comprehension based on the context provided, ensuring it aligns with the topic and level.\n3. **Formulate Question**: Create a robust question that provides clear direction, effectively covering the topic while aligning with the designated level of difficulty.\n4. **Determine Answer**: Generate a concise and accurate answer that relates directly to the question posed and is suitable for the specified difficulty level.\n5. **Construct JSON**: Format the question and answer into the specified JSON structure, ensuring clarity and appropriate guidance.\n\n# Output Format\n\nThe output should be in JSON format with each entry containing:\n- `direction`: A brief and meaningful description of the type of question (e.g., \"Fill in the blanks\", \"Multiple Choice\", or \"Comprehension\").\n- `question`: The question text as a string that provides clear instruction or guidance.\n- `answer`: The correct answer(s), which could be a string or a list of strings for multiple correct answers.\n- `options` (if applicable): A list of possible answer choices for multiple-choice questions.\n\nExample:\n```json\n[\n  {\n    \"direction\": \"Multiple Choice\",\n    \"question\": \"What is the capital of France?\",\n    \"options\": [\"Avignon\", \"Paris\", \"Lyon\", \"Bordeaux\"],\n    \"answer\": \"Paris\"\n  },\n  {\n    \"direction\": \"Fill in the blanks about planet size\",\n    \"question\": \"The largest planet in our solar system is ________.\",\n    \"answer\": \"Jupiter\"\n  },\n  {\n    \"direction\": \"Comprehension based on the passage\",\n    \"question\": \"Read the passage and answer the question: 'In the story, the protagonist is ...'.\",\n    \"answer\": \"The protagonist is a young girl who dreams of becoming an astronaut.\"\n  }\n]\n```\n\n# Notes\n\n- Ensure that the questions are suitable for the specified level of difficulty, providing adequate guidance.\n- Maintain consistency in the answer format aligning with the question type (e.g., a list of options for MCQs)."
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt
                    }
                ]
            },
        ],
        text={
            "format": {
                "type": "text"
            }
        },
        reasoning={},
        tools=[],
        temperature=1,
        max_output_tokens=2048,
        top_p=1,
        store=True
    )

    return response
