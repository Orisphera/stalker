function showOnMap(coords) {
    document.getElementById("map").setAttribute("src",
        "http://static-maps.yandex.ru/1.x/?ll=" + coords + "&spn=0.01,0.01%l=map&pt=" + coords);
}
