from flask import Blueprint, render_template

from functions.upload_file import upload_file


main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def home():
    return render_template('home.html')


@main_bp.route('/upload', methods=['POST'])
def upload():
    return upload_file()
