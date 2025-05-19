import json
import re
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
import jwt
from datetime import datetime, timedelta
from functools import wraps
# Import your watermarking function
from functions.watermark import process_pdf_with_repeating_text_watermark
from functions.s3_delete import delete_pdf_from_s3
from functions.send_email import send_email
from functions.upload_file import upload_file
from functions.lite_llm import get_completion
from functions.open_ai import get_open_ai_completion
from functions.fine_tuning import list_files, upload_file_for_fine_tuning, list_fine_tuning_jobs, delete_model_from_gpt,delete_file_from_openai
import os
from dotenv import load_dotenv
import requests
from functions.config_manager import (
    read_config, write_config, update_config,
    get_available_models, get_default_model,
    get_status_color, get_allowed_extensions,
    get_max_file_size
)

load_dotenv()
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'data', 'config.json')
main_bp = Blueprint('main_bp', __name__)
ALLOWED_ORIGINS = ["https://beta.edhub.school", "https://edhub.school"]
API_KEY = os.getenv("X_API_KEY")
# Change this in production
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")

# Add datetime filter


@main_bp.app_template_filter('datetime')
def format_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user = data['user']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return redirect(url_for('main_bp.login_page'))

        try:
            jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return redirect(url_for('main_bp.login_page'))

        return f(*args, **kwargs)
    return decorated


@main_bp.route('/', methods=['GET'])
def home():
    return render_template('base.html')


@main_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

config = read_config()
@main_bp.route('/data-sets', methods=['GET'])
@login_required
def upload_page():
    try:
        jobs = list_fine_tuning_jobs()
    except Exception as e:
        jobserror = str(e)
    try:
        # Get the list of files
        files_result = list_files()
        config = read_config()
        return render_template('upload.html', files=files_result.get('data', []), jobs=jobs.get('data', []),config=config)
    except Exception as e:
        return render_template('upload.html', files=[], error=str(e))


@main_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user_creds_str = os.getenv("USER_CREDS")
        credentials = json.loads(user_creds_str)

        # Verify credentials
        if username == credentials['username'] and password == credentials['password']:
            # Create JWT token
            token = jwt.encode({
                'user': username,
                'exp': datetime.utcnow() + timedelta(hours=3)
            }, JWT_SECRET, algorithm='HS256')

            response = jsonify({
                'token': token,
                'message': 'Login successful'
            })

            # Set token in HTTP-only cookie
            response.set_cookie(
                'token',
                token,
                httponly=True,
                secure=True,  # For HTTPS
                samesite='Strict',
                max_age=3 * 60 * 60  # 3 hours
            )

            return response, 200
        else:
            return jsonify({
                'error': 'Invalid credentials'
            }), 401

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@main_bp.route('/logout', methods=['POST'])
def logout():
    response = jsonify({'message': 'Successfully logged out'})
    response.delete_cookie('token')
    return response


@main_bp.route('/upload', methods=['POST'])
@token_required
def upload(current_user):
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Call the existing upload_file function
        result = upload_file()

        return jsonify({
            'message': 'File uploaded successfully',
            'details': result
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@main_bp.route('/health', methods=['GET'])
def health_check():
    # Your logic for health check goes here
    # For example, you can check the status of your application, database, etc.

    # Assuming a simple response for a healthy state
    response = {'status': 'OK', 'message': 'Service is healthy'}

    # Return the response as JSON
    return jsonify(response)


@main_bp.route('/watermark', methods=['POST'])
def watermark_pdf():
    data = request.json
    # Extract parameters from the request
    input_pdf_key = data.get('input_pdf_key')
    output_pdf_key = data.get('output_pdf_key')
    watermark_text = data.get('watermark_text')

    # Validate input
    if not all([input_pdf_key, output_pdf_key, watermark_text]):
        return jsonify({'error': 'Missing parameters'}), 400

    try:
        # Call the watermark processing function
        process_pdf_with_repeating_text_watermark(
            input_pdf_key, output_pdf_key, watermark_text)
        return jsonify({'message': 'Watermark added successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/delete-pdf', methods=['POST'])
def delete_pdf():
    # Get the request data (expects a JSON payload)
    data = request.get_json()
    # Extract values from the request JSON body
    pdf_key = data.get('pdf_key')
    # Validate input parameters
    if not all([pdf_key]):
        return jsonify({"error": "Missing required parameters"}), 400

    # Call the function to delete the PDF from S3
    response = delete_pdf_from_s3(pdf_key)

    # Return the response as JSON
    return jsonify(response), 200 if 'message' in response else 500


@main_bp.route('/send-email', methods=['POST'])
def send_email_route():
    try:
        origin = request.headers.get('Origin')
        if origin not in ALLOWED_ORIGINS:
            return jsonify({"error": "Unauthorized domain"}), 403

        data = request.json
        name = data.get('name')
        role = data.get('role')
        contact_number = data.get('contact_number')
        email = data.get('email')
        Source = data.get('Source')

        if not name or not role or not contact_number or not email:
            return jsonify({"error": "Missing required fields"}), 400

        result = send_email(name, role, contact_number, email, Source)
        return jsonify({"message": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_bp.route('/lite-llm-ai', methods=['POST'])
def lite_llm_ai():
    try:
        # Check API key
        api_key = request.headers.get('x-api-key')
        if not api_key or api_key != API_KEY:
            return jsonify({"error": "Invalid or missing X-API-KEY"}), 401

        data = request.json
        prompt = data.get('prompt')
        model = data.get('model', 'gpt-4')  # Default to gpt-4 if not specified

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        response = get_completion(prompt, model)
        return jsonify({"response": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_bp.route('/open-ai', methods=['POST'])
def open_ai():
    try:
        # Check API key
        api_key = request.headers.get('x-api-key')
        if not api_key or api_key != API_KEY:
            return jsonify({"error": "Invalid or missing X-API-KEY"}), 401

        data = request.json
        prompt = data.get('prompt')
        # Get model from config.json, fallback to default if not found
        config = read_config()
        model = data.get('model', config.get('current_model', 'gpt-4o-mini'))

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        response = get_open_ai_completion(prompt, model)
        response_dict = response.dict()
        text = response_dict['output'][0]['content'][0]['text']
        # Step 1: Clean triple backticks
        cleaned = re.sub(r"```json\s*|\s*```", "", text).strip()
        # Step 2: Remove illegal backslashes
        cleaned = re.sub(r'\\(?![\\/"bfnrtu])', '', cleaned)

        # Optional: decode unicode-escaped characters (if needed)
        # cleaned = bytes(cleaned, "utf-8").decode("unicode_escape")  # Only if you're double-escaped
        # Step 3: Parse JSON
        parsed = json.loads(cleaned)
        # Step 4: Wrap in object format if needed
        if isinstance(parsed, list):
            return jsonify({"questions": parsed}), 200
        else:
            return jsonify(parsed), 200

    except json.JSONDecodeError as e:
        return jsonify({"error": f"JSON decode error: {str(e)}", "raw": cleaned}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    # If the result is a list, convert to object format
   
        # return parsed
        # return jsonify(data), 200
        # data = json.loads(text)
        # match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)

        # if match:
        #     json_text = match.group(1)
        #     # Step 2: Convert to Python object
        #     data = json.loads(json_text)
        #     return jsonify(data), 200
        # else:
        #     data = json.loads(text)
        #     return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_bp.route('/fine-tune-upload', methods=['POST'])
@token_required
def fine_tune_upload(current_user):
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Save the file temporarily
        temp_path = os.path.join('/tmp', file.filename)
        file.save(temp_path)

        try:
            # Upload to OpenAI
            result = upload_file_for_fine_tuning(temp_path)

            # Clean up temporary file
            os.remove(temp_path)

            return jsonify({
                'message': 'File uploaded successfully for fine-tuning',
                'details': result
            }), 200

        except Exception as e:
            # Clean up temporary file in case of error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@main_bp.route('/delete-model', methods=['POST'])
@token_required
def delete_model(current_user):
    data = request.json
    model_id = data.get('model_id')  # Correct key
    print(model_id)
    if not model_id:
        return jsonify({'error': 'Missing file ID'}), 400

    try:
        result = delete_model_from_gpt(model_id)  # Use new helper function
        return jsonify({'status': 'deleted', 'result': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/delete-file', methods=['POST'])
@token_required
def delete_file(current_user):
    data = request.json
    file_id = data.get('file_id')  # Correct key
    print(file_id)
    if not file_id:
        return jsonify({'error': 'Missing file ID'}), 400

    try:
        result = delete_file_from_openai(file_id)  # Use new helper function
        return jsonify({'status': 'deleted', 'result': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# @main_bp.route('/fine-tune', methods=['POST'])
# @token_required
# def fine_tune_model(current_user):
#     try:
#         data = request.get_json()
#         # Add your fine-tuning logic here
#         return jsonify({
#             'message': 'Model fine-tuning started',
#             'user': current_user
#         }), 200
#     except Exception as e:
#         return jsonify({
#             'error': str(e)
#         }), 500


@main_bp.route('/create-training-job', methods=['POST'])
@token_required
def create_training_job(current_user):
    try:
        data = request.get_json()
        training_file = data.get('training_file')
        model = data.get('model', 'gpt-4o-mini-2024-07-18')

        if not training_file:
            return jsonify({'error': 'Training file ID is required'}), 400

        # Read existing config
        config = read_config()

        # Append training_file if not already in used_data_set
        if 'used_data_set' not in config:
            config['used_data_set'] = []

        if training_file not in config['used_data_set']:
            config['used_data_set'].append(training_file)
            write_config(config)

        # Get API key from environment variables
        api_key = os.getenv('GPT_API_KEY')
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables")

        # OpenAI API endpoint for creating fine-tuning jobs
        url = "https://api.openai.com/v1/fine_tuning/jobs"

        # Make the API request
        # response = requests.post(
        #     url,
        #     headers={
        #         'Authorization': f'Bearer {api_key}',
        #         'Content-Type': 'application/json'
        #     },
        #     json={
        #         'training_file': training_file,
        #         'model': model
        #     }
        # )

        # Check if the request was successful
        # response.raise_for_status()

        return jsonify({'message': f'insert this ID {training_file} in used_data_set'}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error creating training job: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@main_bp.route('/fine-tuning', methods=['GET'])
@login_required
def jobs_page():
    try:
        jobs = list_fine_tuning_jobs()
        config = read_config()
        current_model = config.get('current_model', 'gpt-4o-mini')
        return render_template('jobs.html', jobs=jobs.get('data', []), current_model=current_model)
    except Exception as e:
        return render_template('jobs.html', jobs=[], error=str(e))


@main_bp.route('/config/current_model', methods=['PUT'])
@token_required
def update_current_model(current_user):
    try:
        data = request.get_json()
        if not data or 'value' not in data:
            return jsonify({'error': 'No model value provided'}), 400

        model = data['value']
        success = update_config('current_model', model)

        if success:
            return jsonify({'message': f'Current model updated to {model}'}), 200
        else:
            return jsonify({'error': 'Failed to update current model'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/playground', methods=['GET'])
@login_required
def playground():
    try:
        jobs = list_fine_tuning_jobs()
        config = read_config()
        current_model = config.get('current_model', 'gpt-4o-mini')
        return render_template('playground.html',
                               jobs=jobs.get('data', []),
                               current_model=current_model,
                               api_key=API_KEY)
    except Exception as e:
        return render_template('playground.html',
                               jobs=[],
                               current_model='gpt-4o-mini',
                               error=str(e),
                               api_key=API_KEY)
