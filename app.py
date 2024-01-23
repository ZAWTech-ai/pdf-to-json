
import os
import awsgi
from flask import Flask
from flask_cors import CORS
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from routes import main_bp

app = Flask(__name__)
CORS(app)
app.register_blueprint(main_bp)


class MyHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return
        print(
            f'Restarting the Flask server due to file change: {event.src_path}')
        os.system('python app.py')


def lambda_handler(event, context):
    return awsgi.response(app, event, context, base64_content_types={"image/png"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

