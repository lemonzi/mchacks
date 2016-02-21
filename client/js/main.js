SAMPLE_DURATION = 3000;

$(function() {

    var ctx = new AudioContext();

    Webcam.set({
        audio: true,
        image_format: 'jpeg',
        jpeg_quality: 85,
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
        getWAVBlob({
            ctx: ctx,
            duration: SAMPLE_DURATION,
            stream: Webcam.stream
        }, function(audio_blob) {
            console.log("Got the audio", audio_blob);
            Webcam.snap(function(snap) {
                // var raw = snap.replace(/^data\:image\/\w+\);base64\,/, '');
                // var arr = [Webcam.base64DecToArr(raw)];
                // var photo_blob = new Blob(arr, {type: 'image/jpeg'});
                // console.log("Got the image", photo_blob);
                // var img = document.querySelector('#test-img');
                // img.src = URL.createObjectURL(photo_blob);
                fd = new FormData();
                //fd.append('photo', photo_blob);
                fd.append('photo', snap);
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
            });
        });
    });

});

