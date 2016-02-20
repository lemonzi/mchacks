SAMPLE_DURATION = 2000;

$(function() {

    var ctx = new AudioContext();

    Webcam.set({audio: true});
    Webcam.attach('.camera-preview');

    $('.record-btn').click(function startRecording() {
        getWAVBlob({
            ctx: ctx,
            duration: SAMPLE_DURATION,
            stream: Webcam.stream
        }, function(blob) {
            // prepare WAV for server
            console.log("Got the audio", blob);
        });
        Webcam.snap(function(data_uri) {
            // prepare image for server
            console.log("Got the image, with size", data_uri.length);
        });
    });

});

