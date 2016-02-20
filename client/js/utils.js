/**
 * Some utilities
 */

// Prefix shims
window.AudioContext = window.AudioContext || window.webkitAudioContext;
navigator.getUserMedia = 
    navigator.getUserMedia || 
    navigator.webkitGetUserMedia || 
    navigator.mozGetUserMedia || 
    navigator.msGetUserMedia ||
    alert("getUserMedia not supported, sorry!");


function getWAVBlob(opts, callback) {
    console.log("Getting access to the microphone...");
    console.log("Got the microphone");
    var source = opts.ctx.createMediaStreamSource(opts.stream);
    var recorder = new Recorder(source);
    recorder.record();
    console.log("Recording...");
    setTimeout(function stopRecording() {
        console.log("Recording timeout");
        recorder.stop();
        recorder.exportWAV(callback);
    }, opts.duration);
}

