let center_latitude = <latt>;
let center_longitude = <long>;
let span = 0.01;


function updateMap() {
    const map = document.getElementById("map")
    map.setAttribute("src", "http://static-maps.yandex.ru/1.x/?ll="+center_longitude+","+center_latitude+
        "&spn="+span+","+span+"&l=map&pt=<marks>");
}


function on_load() {
    updateMap()
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
    center_latitude += span / 3;
    updateMap();
}

function moveLeft() {
    center_longitude -= span * 2 / 3;
    updateMap();
}

function moveRight() {
    center_longitude += span * 2 / 3;
    updateMap();
}

function zoomIn() {
    span /= 2.15;
    updateMap();
}

function moveDown() {
    center_latitude -= span / 3;
    updateMap();
}

function zoomOut() {
    span *= 2.15;
    updateMap();
}
