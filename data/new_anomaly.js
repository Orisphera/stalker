function onload() {
    function success(position) {
        document.getElementById("latt_deg").value = position.coords.latitude;
        document.getElementById("latt_min").value = 0;
        document.getElementById("latt_sec").value = 0;
        document.getElementById("long_deg").value = position.coords.longitude;
        document.getElementById("long_min").value = 0;
        document.getElementById("long_sec").value = 0;
    }

    function error() {}

    if(navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(success, error);
    }
}

function getFloat(id) {
    return parseFloat(document.getElementById(id).value)
}

function showOnMap1() {
    showOnMap((getFloat("long_deg") + (getFloat("long_min") + getFloat("long_sec") / 60) / 60) + "," +
              (getFloat("latt_deg") + (getFloat("latt_min") + getFloat("latt_sec") / 60) / 60));
}
