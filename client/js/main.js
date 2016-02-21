// canvas.toBlob polyfill
if (!HTMLCanvasElement.prototype.toBlob) {
 Object.defineProperty(HTMLCanvasElement.prototype, 'toBlob', {
  value: function (callback, type, quality) {

    var binStr = atob( this.toDataURL(type, quality).split(',')[1] ),
        len = binStr.length,
        arr = new Uint8Array(len);

    for (var i=0; i<len; i++ ) {
     arr[i] = binStr.charCodeAt(i);
    }

    callback( new Blob( [arr], {type: type || 'image/png'} ) );
  }
 });
}

SAMPLE_DURATION = 2000;

$(function() {

    var ctx = new AudioContext();

    Webcam.set({
        audio: true,
        image_format: 'jpeg',
        jpeg_quality: 70,
        // live preview size
        width: 320,
        height: 240,
        // device capture size
        dest_width: 320,
        dest_height: 240,
        // final cropped size
        crop_width: 240,
        crop_height: 240
    });

    Webcam.attach('.camera-preview');

    $('.record-btn').click(function startRecording() {
        if ($('.record-btn').hasClass('recording')) {
            return;
        }
        $('.record-btn').addClass('recording');
        getWAVBlob({
            ctx: ctx,
            duration: SAMPLE_DURATION,
            stream: Webcam.stream
        }, function(audio_blob) {
            console.log("Got the audio", audio_blob);
            Webcam.snap(function(snap, canvas) {
                $('.record-btn').removeClass('recording');
                canvas.toBlob(function(photo_blob) {
                    console.log("Got the snap", photo_blob);
                    fd = new FormData();
                    fd.append('photo', photo_blob);
                    fd.append('audio', audio_blob);
                    $.ajax({
                        url: '/upload',
                        data: fd,
                        processData: false,
                        contentType: false,
                        type: 'POST',
                        success: function(data){
                            // yaaay
                        }
                    });
                }, 'image/jpeg', 0.7);
            });
        });
    });

});

