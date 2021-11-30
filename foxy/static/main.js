const socket = io();

socket.on('list connected', (list) => {
    all_status = document.getElementsByClassName("status");
    for (let elem of all_status) {
        elem.classList.remove("green");
        elem.classList.add("red");
    }
    for (let player_id of list) {
        all_items = document.getElementsByClassName("u" + player_id);
        for (let elem of all_items) {
            elem.classList.add("green");
            elem.classList.remove("red");
        }
    }
});
