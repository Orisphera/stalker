function toRiddlePage() {
    window.location.href = "/riddles/" + document.getElementById("riddle_id").value;
}

function toUserPage() {
    window.location.href = "/users/" + document.getElementById("user_id").value;
}
