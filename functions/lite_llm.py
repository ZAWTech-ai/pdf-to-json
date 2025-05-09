import os 
from litellm import completion, responses
from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("GPT_API_KEY")

def get_completion(prompt: str, model: str = "gpt-4") -> str:
    """
    Get completion from the specified model using the given prompt.
    
    Args:
        prompt (str): The input prompt to send to the model
        model (str): The model to use for completion (default: "gpt-4")
        
    Returns:
        str: The model's response
    """
    response = completion(
        model=model,
        messages=[{"content": prompt, "role": "user"}]
    )
    return response.choices[0].message.content

def get_responses(prompt: str, model: str = "gpt-4") -> str:
    """
    Get response from the specified model using the given prompt.

      Args:
        prompt (str): The input prompt to send to the model
        model (str): The model to use for completion (default: "gpt-4")
        
    Returns:
        str: The model's response
    """
    response = responses(
        model=model,
        messages=[{"content": prompt, "role": "user"}]
    )
    return response.choices[0].message.content

# Example usage:
# response = get_completion("Hello, how are you?", "gpt-4")