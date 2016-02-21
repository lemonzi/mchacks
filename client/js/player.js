var ctx = new AudioContext();

var masterVolume = ctx.createGainNode();
masterVolume.gain.value = 1;
masterVolume.connect(ctx.destination);

// This is the map we'll be using the playback
var players = {};

// Pre-fill it with some samples
samples = {
    1: '1.wav', 
    2: '2.wav'
};
for (var key in samples) {
    var source = ctx.createBufferSource();
    source.connect(masterVolume);
    $.ajax({
        dataType:'blob',
        type:'GET',
        url:'/data' + samples[key]
    }).done(function(blob) {
        ctx.decodeAudioData(buffer, function(res) {
            source.buffer = res;
            source.ready = true;
        });
    });
    players[key] = source;
});


function midiStream(buffer) {
    // Creating the MIDIFile instance
    var midiFile = new MIDIFile(buffer);

    // Reading metadata
    var nTracks = midiFile.header.getTracksCount();

    // We can create a stream for each track
    var trackEventsChunk = midiFile.getTrackEvents(0);
    var events = new MIDIFile.createParser(trackEventsChunk);

    return events;
}

function playStream(events) {
    var timeOrigin = ctx.currentTime;
    while (var ev = events.next()) {
        if (ev.type === MIDIFile.EVENT_MIDI_NOTE_ON) {
            var pitch = ev.param1;
            var time = ev.playTime;
            var channel = ev.channel; // just in case... (drumkit?)
            var vel = ev.param2;      // for fancy WebAudio Gainz
            var when = timeOrigin + time;
            players[pitch].source.play(when);
            images[pitch].show(when);
        }
    }
}
