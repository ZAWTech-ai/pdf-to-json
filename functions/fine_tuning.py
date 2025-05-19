import os
import requests
from dotenv import load_dotenv
from flask import jsonify
load_dotenv()


def upload_file_for_fine_tuning(file_path):
    """
    Upload a file to OpenAI for fine-tuning.

    Args:
        file_path (str): Path to the file to be uploadedx

    Returns:
        dict: Response from OpenAI API containing file details
    """
    try:
        # Get API key from environment variables
        api_key = os.getenv('GPT_API_KEY')
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables")

        # OpenAI API endpoint for file uploads
        url = "https://api.openai.com/v1/files"

        # Prepare the file for upload
        with open(file_path, 'rb') as file:
            files = {
                'file': (os.path.basename(file_path), file),
                'purpose': (None, 'fine-tune')
            }

            # Make the API request
            response = requests.post(
                url,
                headers={
                    'Authorization': f'Bearer {api_key}'
                },
                files=files
            )

            # Check if the request was successful
            response.raise_for_status()

            return response.json()

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error uploading file to OpenAI: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")


def list_files():
    """
    List all files uploaded to OpenAI for fine-tuning.

    Returns:
        dict: Response from OpenAI API containing list of files
    """
    try:
        # Get API key from environment variables
        api_key = os.getenv('GPT_API_KEY')
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables")

        # OpenAI API endpoint for listing files
        url = "https://api.openai.com/v1/files"

        # Make the API request
        response = requests.get(
            url,
            headers={
                'Authorization': f'Bearer {api_key}'
            }
        )

        # Check if the request was successful
        response.raise_for_status()
        response_data = response.json()
        files_list = response_data.get("data", [])
        # Step 2: Filter out .csv files
        filtered_files = [
            file for file in files_list
            if not file.get('filename', '').endswith('.csv')
        ]

        # Step 3: Return filtered files
        return {"data": filtered_files}

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error listing files from OpenAI: {str(e)}")
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def list_fine_tuning_jobs():
    """
    List all fine-tuning jobs from OpenAI.

    Returns:
        dict: Response from OpenAI API containing list of fine-tuning jobs
    """
    try:
        # Get API key from environment variables
        api_key = os.getenv('GPT_API_KEY')
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables")

        # OpenAI API endpoint for listing fine-tuning jobs
        url = "https://api.openai.com/v1/fine_tuning/jobs"

        # Make the API request
        response = requests.get(
            url,
            headers={
                'Authorization': f'Bearer {api_key}'
            }
        )

        # Check if the request was successful
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error listing fine-tuning jobs: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")

def delete_model_from_gpt(model_id):
    """
    Delete a model from OpenAI's servers.
    """
    try:
        api_key = os.getenv('GPT_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        url = f"https://api.openai.com/v1/models/{model_id}"

        response = requests.delete(
            url,
            headers={
                'Authorization': f'Bearer {api_key}'
            }
        )

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error deleting file from OpenAI: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")


def delete_file_from_openai(file_id):
    """
    Delete a file from OpenAI's servers.
    """
    try:
        api_key = os.getenv('GPT_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        url = f"https://api.openai.com/v1/files/{file_id}"

        response = requests.delete(
            url,
            headers={
                'Authorization': f'Bearer {api_key}'
            }
        )

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error deleting file from OpenAI: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")
