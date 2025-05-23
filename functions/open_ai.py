import os
from flask import jsonify
from openai import OpenAI
from prompts.gen_ai_system_prompt import gen_ai_system_prompt
from prompts.user_prompt_post_fix import user_prompt_post_fix
import json
from dotenv import load_dotenv


load_dotenv()


client = OpenAI(api_key=os.getenv("GPT_API_KEY"))


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

    full_prompt = f"{prompt}{user_prompt_post_fix}"
    print(full_prompt)
    response = client.responses.create(
        model=model,
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
                        "text": full_prompt
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
