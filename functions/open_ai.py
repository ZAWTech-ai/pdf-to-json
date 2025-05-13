from flask import jsonify
from openai import OpenAI
from prompts.gen_ai_system_prompt import gen_ai_system_prompt
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
                        "text": gen_ai_system_prompt
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
