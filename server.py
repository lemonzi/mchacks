import os
import flask
import base64
import audio_dsp

app = flask.Flask(__name__, static_url_path='', static_folder='client')
app.config['UPLOAD_FOLDER'] = 'data/'
app.config['data'] = {}

@app.before_first_request
def construct_datamodel():
    data = {}

    for file in os.listdir("data"):
        if len(file) > 10 and file[-4:] == '.wav':
            file = file[:-4]    # remove ending
            tmp = file.split('_')
            sound = tmp[0]
            midi_node = tmp[1]
            epoch_time = tmp[2]
            if (sound, midi_node) not in data:
                audio_name = file + '.wav'
                image_name = epoch_time + '.jpeg'
                data[(sound, midi_node)] = [(audio_name, image_name)]
            else:
                data[(sound, midi_node)].append((audio_name, image_name))
    
    app.config['data'] = data


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


@app.route('/samples/<sound>/<pitch>')
def uploaded_file(sound, pitch):
    """ Choose a sound with a given MIDI node. 
    Return a tuple of audio- and image filenames """

    data = app.config['data']

    try:
        t = data[(sound, pitch)]
    except Exception, e:
        #raise
        print "MIDI node {} with sound {} not found!".format(pitch, sound)
    else:
        filename = random.choose(t)

    return flask.send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("8000"),
        debug=True
    )
