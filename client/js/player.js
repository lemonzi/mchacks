$(function() {

    var ctx = new AudioContext();

    var masterVolume = ctx.createGain();
    masterVolume.gain.value = 0.5;
    masterVolume.connect(ctx.destination);

    gridData = {};
    initGrid(12);

    // This is the map we'll be using for playback
    var buffers = {};

    function reloadBufferRange(begin, end) {
        // Pre-fill it with some samples
        var toLoad = [];
        for (var i = begin; i < end; i++) {
            toLoad.push(i);
        }
        toLoad.forEach(function(i) {
            $.getNative('/samples/sing/' + i, function(buffer) {
                ctx.decodeAudioData(buffer, function(res) {
                    buffers[i] = res;
                }, function(e) { console.log('error') });
            });
        });
    }

    reloadBufferRange(20, 95);

    //setInterval(function(){reloadBufferRange(20, 95)}, 2000);

    $.getNative('/midi/zankarland.mid', function(data) {
        setTimeout(function() {
            playWrapper(midiStream(data));
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
        playState.faces = [];
        playAsyncStream();
    }

    function playAsyncStream() {
        var timeElapsed = ctx.currentTime - playState.timeOrigin;
        var eventsToPlay = playState.events.filter(function(ev) {
            return (ev.playTime/1000) < (timeElapsed + 1);
        });
        playState.events = playState.events.filter(function(ev) {
            return (ev.playTime/1000) >= (timeElapsed + 1);
        });
        setTimeout(playAsyncStream, 1000);
        if (eventsToPlay.length > 0)
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
            playState.faces.push({time: when, pitch: pitch});
        });
    }

    /*
     * vizz
     */


    function initGrid(nElements) {
        gridData.nElements = nElements;
        var container = $('.faces');
        for (var i = 0; i < nElements; i++) {
            var element = $('<div>');
            element.addClass('face');
            element.addClass('idx'+i);
            container.append(element);
        }
    }

    function faceForNote(pitch) {
        var url = '/images/sing/' + pitch;
        var id = Math.floor(Math.random() * gridData.nElements);
        var face = $('.face.idx' + id);
        face.css('background-image', 'url('+url+')');
    }

    requestAnimationFrame(function renderingCallback() {
        // this is our rendering callback that checks everything
        try {
            var now = ctx.currentTime;
            if (playState.faces) {
                var newFrames = playState.faces.forEach(function(f) {
                    if (f.time < now) {
                        faceForNote(f.pitch);
                    }
                });
                playState.faces = playState.faces.filter(function(f) {
                    return f.time >= now;
                })
            }
        } finally {
            requestAnimationFrame(renderingCallback);
        }
    });

});

