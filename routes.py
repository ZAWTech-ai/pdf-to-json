from flask import Blueprint, request, jsonify
from functions.watermark import process_pdf_with_repeating_text_watermark  # Import your watermarking function
from functions.s3_delete import delete_pdf_from_s3
from functions.upload_file import upload_file


main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/upload', methods=['POST'])
def upload():
    return upload_file()


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
    if not all([ input_pdf_key, output_pdf_key, watermark_text]):
        return jsonify({'error': 'Missing parameters'}), 400

    try:
        # Call the watermark processing function
        process_pdf_with_repeating_text_watermark('edhubshop', input_pdf_key, output_pdf_key, watermark_text)
        return jsonify({'message': 'Watermark added successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/delete-pdf', methods=['POST'])
def delete_pdf():
    # Get the PDF key from the request
    data = request.get_json()
    pdf_key = data.get('pdf_key')

    if not pdf_key:
        return jsonify({'error': 'PDF key is required'}), 400

    try:
        # Delete the object from the S3 bucket
        s3.delete_object(Bucket='edhubshop', Key=pdf_key)
        return jsonify({'message': f'{pdf_key} deleted successfully'}), 200

    except NoCredentialsError:
        return jsonify({'error': 'Credentials not available'}), 403

    except ClientError as e:
        return jsonify({'error': f'Failed to delete PDF: {str(e)}'}), 500


@app.route('/delete-pdf', methods=['POST'])
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
