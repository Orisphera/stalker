function onload() {
    function success(position) {
        document.getElementById("latt").value = position.coords.latitude;
        document.getElementById("long").value = position.coords.longitude;
    }

    function error() {}

    if(navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(success, error);
    }
}
