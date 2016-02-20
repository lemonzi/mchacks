import os
import flask

app = flask.Flask(__name__, static_url_path='', static_folder='client')

app.config['UPLOAD_FOLDER'] = 'data/'
app.config['ALLOWED_EXTENSIONS'] = {'wav', 'jpeg'}


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    audio = flask.request.files['audio']
    if audio:
        print("Received an audio file")
        filename = 'whatever'
        audio.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    photo = flask.request.files['photo']
    if photo:
        print("Received an image")
        filename = 'whatever'
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return 'Loaded data'


@app.route('/assets/<filename>')
def uploaded_file(filename):
    return flask.send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("8000"),
        debug=True
    )
