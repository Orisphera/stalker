function getFloat(id) {
    return parseFloat(document.getElementById(id).value)
}

function showOnMap1() {
    showOnMap((getFloat("long_deg") + (getFloat("long_min") + getFloat("long_sec") / 60) / 60) + "," +
              (getFloat("latt_deg") + (getFloat("latt_min") + getFloat("latt_sec") / 60) / 60));
}
