from flask import Blueprint

from functions.upload_file import upload_file


main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/upload', methods=['POST'])
def upload():
    return upload_file()
