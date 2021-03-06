import os
import flask
import base64
import audio_dsp
import random
from collections import defaultdict

app = flask.Flask(__name__, static_url_path='', static_folder='client')
app.config['UPLOAD_FOLDER'] = 'data/'
app.config['data'] = defaultdict(list)


@app.before_first_request
def construct_datamodel():
    new_dataset = defaultdict(list)
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if len(filename) > 10 and filename[-4:] == '.mp3':
            filename = filename[:-4] # remove ending
            tmp = filename.split('_')
            sound = tmp[0]
            midi_node = tmp[1]
            epoch_time = tmp[2]
            audio_name = filename + '.mp3'
            image_name = sound + '_' + epoch_time + '.jpeg'
            new_dataset[(sound, midi_node)].append((audio_name, image_name))
    app.config['data'] = new_dataset


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/player')
def player():
    return app.send_static_file('player.html')


@app.route('/upload', methods=['POST'])
def upload():
    req = flask.request
    if 'audio' not in req.files or 'photo' not in req.files:
        return flask.make_response('Error: malformed request', 400)
    id = 'sing'  # make an id
    location = os.path.join(app.config['UPLOAD_FOLDER'], id)
    audio = req.files['audio']
    midi_list, timestamp = audio_dsp.process_audio(audio, sound=location)
    photo_fn = '{}_{}.jpeg'.format(id,timestamp)
    for m in midi_list:
        audio_fn = '{}_{}_{}.mp3'.format(id,m,timestamp)
        app.config['data'][(id,str(m))].append((audio_fn, photo_fn))
    photo = req.files['photo']
    photo.save('{}_{}.jpeg'.format(location, timestamp));
    construct_datamodel()
    return 'Loaded data'


@app.route('/samples/<sound>/<pitch>')
def uploaded_file(sound, pitch):
    """ Choose a sound with a given MIDI node.
    Return a tuple of audio- and image filenames """
    t = app.config['data'][(sound, str(pitch))]
    if t:
        filename = random.choice(t)
        return flask.send_from_directory(app.config['UPLOAD_FOLDER'], filename[0], cache_timeout=1)
    else:
        return flask.make_response('Sample not found', 404)


@app.route('/images/<sound>/<pitch>')
def uploaded_photo(sound, pitch):
    t = app.config['data'][(sound, str(pitch))]
    if t:
        filename = random.choice(t)
        return flask.send_from_directory(app.config['UPLOAD_FOLDER'], filename[1], cache_timeout=1)
    else:
        return flask.make_response('Sample not found', 404)


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("8000"),
        debug=True
    )
