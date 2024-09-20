from flask import Blueprint, jsonify
from functions.watermark import process_pdf_with_repeating_text_watermark  # Import your watermarking function

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
    input_pdf_key = data.get('1686320832546-G2 Week 41 (revised 2022-2023) (74WVX).pdf')
    output_pdf_key = data.get('watermark_test1.pdf')
    watermark_text = data.get('Confidential')

    # Validate input
    if not all([bucket_name, input_pdf_key, output_pdf_key, watermark_text]):
        return jsonify({'error': 'Missing parameters'}), 400

    try:
        # Call the watermark processing function
        process_pdf_with_repeating_text_watermark(bucket_name, input_pdf_key, output_pdf_key, watermark_text)
        return jsonify({'message': 'Watermark added successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500