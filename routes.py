from flask import Blueprint, jsonify

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
