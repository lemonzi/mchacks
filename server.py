import os
import flask
import base64
import audio_dsp

app = flask.Flask(__name__, static_url_path='', static_folder='client')
app.config['UPLOAD_FOLDER'] = 'data/'


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/player')
def player():
    return app.send_static_file('player.html')


@app.route('/upload', methods=['POST'])
def upload():
    req = flask.request
    if 'audio' not in req.files or 'photo' not in req.values:
        return 'Error: malformed request', 400
    id = 42  # make an id
    location = os.path.join(app.config['UPLOAD_FOLDER'], str(id))
    audio = req.files['audio']
    audio_dsp.process_audio(audio, prefix=location)
    photo = req.values['photo']
    # photo.save(location+'.jpeg')
    with open(location+'.jpeg', 'w') as fd:
        fd.write(base64.b64decode(photo))
    return 'Loaded data'


@app.route('/samples/<pitch>')
def uploaded_file(pitch):
    filename = '42_{}.wav'.format(pitch)
    return flask.send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("8000"),
        debug=True
    )
