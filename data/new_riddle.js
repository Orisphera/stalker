function on_load() {
    function success(position) {
        document.getElementById("latt_deg").value = position.coords.latitude;
        document.getElementById("long_deg").value = position.coords.longitude;
    }

    function error() {}

    if(navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(success, error);
    }
}
