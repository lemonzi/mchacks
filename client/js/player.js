$(function() {

    var ctx = new AudioContext();

    var masterVolume = ctx.createGain();
    masterVolume.gain.value = 0.5;
    masterVolume.connect(ctx.destination);

    // This is the map we'll be using for playback
    var buffers = [];

    function reloadBufferRange(begin, end) {
        // Pre-fill it with some samples
        var toLoad = [];
        for (var i = begin; i < end; i++) {
            toLoad.push(i);
        }
        toLoad.forEach(function(i) {
            $.getNative('/samples/' + i, function(buffer) {
                ctx.decodeAudioData(buffer, function(res) {
                    buffers[i] = res;
                });
            });
        });
    }

    reloadBufferRange(20, 80);

    setInterval(function(){reloadBufferRange(20,80)}, 5000);

    $.getNative('/midi/zankarland.mid', function(data) {
        setTimeout(function() {
            playStream(midiStream(data));
        }, 2000);
    });

    function midiStream(buffer) {
        var midiFile = new MIDIFile(buffer);
        var events = midiFile.getMidiEvents().filter(function(ev) {
            return ev.type == 0x8 && ev.subtype == 0x9 && ev.channel != 10;
        });
        return events;
    }

    playState = {};
    function playWrapper(events) {
        playState.events = events;
        playState.timeOrigin = ctx.currentTime + 0.3;
        playAsyncStream();
    }

    function playAsyncStream() {
        var timeElapsed = ctx.currentTime - playState.timeOrigin;
        var eventsToPlay = playState.events.filter(function(ev) {
            return ev.playTime < (timeElapsed + 1000);
        });
        playState.events = playState.events.filter(function(ev) {
            return ev.playTime >= (timeElapsed + 1000);
        });
        setTimeout(playAsyncStream, 1000);
        playStream(eventsToPlay);
    }

    function playStream(events) {
        events.filter(function(ev) { 
            return ev.channel != 10;
        }).forEach(function(ev) {
            var pitch = ev.param1;
            var time = ev.playTime / 1000;
            console.log("Playing " + pitch + " at time " + time);
            var channel = ev.channel; // just in case... (drumkit?)
            var vel = ev.param2;      // for fancy WebAudio Gainz
            var when = playState.timeOrigin + time;
            var source = ctx.createBufferSource();
            buffer = buffers[pitch];
            if (buffer) {
                source.buffer = buffer;
                source.connect(masterVolume);
                source.start(when);
            } else {
                console.log('buffer empty...');
            }
            // images[pitch].show(when);
        });
    }

});

