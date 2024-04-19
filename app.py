from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/upload-video', methods=['POST'])
def upload_video():
    video = request.files['video']
    if video:
        filename = secure_filename(video.filename)
        video.save(os.path.join('./upload-video', filename))
        return 'Видео успешно загружено', 200
    return 'Ошибка при загрузке видео', 400

if __name__ == '__main__':
    app.run(debug=True)

