import json
from openai import OpenAI

from typing import Dict, List
import re
import os
from ast import literal_eval
from dotenv import load_dotenv

load_dotenv()

# Configure OpenAI API key
  # Replace with your actual API key

def extract_questions_answers(pdf_data: Dict) -> List[Dict[str, str]]:
    client = OpenAI(api_key=os.getenv("GPT_API_KEY"))
    """
    Extracts questions and answers from PDF data using the OpenAI GPT API.
    
    Args:
        pdf_data (Dict): JSON data containing PDF text content as provided.
        
    Returns:
        List[Dict[str, str]]: List of dictionaries with direction, question, and answer.
    """
    # Convert the PDF data to a string for the GPT prompt
    pdf_data_str = json.dumps(pdf_data, indent=2)

    # Construct the prompt for the GPT API
    prompt = f"""
    You are a data extraction assistant. I have provided JSON data extracted from a PDF document containing questions and answers related to imperatives, school rules, and other instructions. The questions typically contain blanks (e.g., '________________') that need to be filled in, and the answers are often provided in red text (color '#e42137' or '#e42036'). Your task is to extract the questions and their corresponding answers, along with the relevant directions, and return them in a JSON array of objects with the following format:

    [
        {{
            "direction": "The instruction or context for the question",
            "question": "The question text with blanks",
            "answer": "The answer that fills the blanks"
        }},
        ...
    ]

    ### Instructions:
    1. Identify questions by looking for text containing blanks (e.g., '________________', '___________', etc.).
    2. Extract the corresponding answers, typically found in red-colored text ('#e42137' or '#e42036').
    3. Include the direction or context, which is usually the instructional text preceding the questions (e.g., "Look at the school rules. Fill in the blanks.").
    4. Replace curly apostrophes (') with straight apostrophes (') in the output (e.g., 'mustn't' instead of 'mustn’t').
    5. Handle cases where questions have multiple blanks (e.g., 'We _____________ run _____________ in the corridor.') by combining the answers into a single string (e.g., 'mustn't around').
    6. Correct any obvious typos in the answers (e.g., 'Dont not feed' should be 'Do not feed').
    7. Ensure the output is a valid JSON array of objects, with each object containing 'direction', 'question', and 'answer'.
    8. Process the questions in the order they appear in the document, grouping them by section (e.g., School Rules, Park Rules, etc.).
    9. For sections marked as "Answers may vary. Suggested answers only," use the provided answers as-is.

    ### Input Data:
    ```json
    {pdf_data_str}
    ```
    
    ### Output:
    Return a JSON array of objects in the specified format. Ensure the response is clean and contains only the JSON array, without additional text or explanations.
    """
    # return prompt
    # Call the OpenAI GPT API
    print("Calling GPT API...")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use an appropriate model
            messages=[
                {"role": "system", "content": "You are a precise data extraction assistant. Follow the instructions exactly and return only the requested JSON output."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # Low temperature for precise output
            max_tokens=4000   # Adjust based on expected response length
        )
        # Extract the response content
        response_content = response.choices[0].message.content.strip()

        # Ensure the response is valid JSON

        return response_content
        try:
            result = json.loads(response_content)

            # # Post-process to replace curly apostrophes with straight apostrophes
            # for item in result:
            #     item["answer"] = re.sub(r"’", "'", item["answer"])
            #     item["question"] = re.sub(r"’", "'", item["question"])
            #     item["direction"] = re.sub(r"’", "'", item["direction"])

            return result
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON response from GPT API: {e}")
            return []

    except Exception as e:
        print(f"Error calling GPT API: {e}")
        return []

