gridData = {};

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
    face.removeClass('faded');
    face.css('background-image', 'url('+url+')');
    face.addClass('faded');
}

