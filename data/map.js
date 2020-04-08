let center_latitude = 0;
let center_longitude = 0;
let span = 0.01;


function updateMap() {
    const map = document.getElementById("map")
    map.setAttribute("src", "http://static-maps.yandex.ru/1.x/?ll="+center_longitude+","+center_latitude+
        "&spn="+span+","+span+"&l=map&pt=<marks>");
}


function onload() {
    function success(position) {
        center_latitude = position.coords.latitude;
        center_longitude = position.coords.longitude;
        updateMap();
    }

    function error() {}

    if(navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(success, error);
    }
}


function moveUp() {
    center_latitude += span / 2;
    updateMap();
}

function moveLeft() {
    center_longitude -= span;
    updateMap();
}

function moveRight() {
    center_longitude += span;
    updateMap();
}

function zoomIn() {
    span /= 10;
    updateMap();
}

function moveDown() {
    center_latitude -= span / 2;
    updateMap();
}

function zoomOut() {
    span *= 10;
    updateMap();
}



