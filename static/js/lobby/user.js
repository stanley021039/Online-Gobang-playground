showLobby = function(inputUsername){
    socket.connect();
    // socket.on("connect", function() {
    // })
    socket.emit("user_join_lobby", inputUsername);
    socket.on("user_join_lobby_response", function(response) {
        responseAccept = response["accept"]
        if (responseAccept){
            username = inputUsername
            console.log(`${username} join lobby`);
            document.getElementById("page-container").style.display = "block";
            document.getElementById("chat").style.display = "block";
            document.getElementById("landing").style.display = "none";
        } else {
            console.log(response.message);
            socket.disconnect();
            document.getElementById("user-exists-msg").style.display = "block";
        }
    });
}

// 用戶加入-emit
document.getElementById("join-btn").addEventListener("click", function() {
    var inputUsername = document.getElementById("username").value;
    showLobby(inputUsername)
})

if (username !== "None") {
    showLobby(username)
}

//上傳訊息-emit
document.getElementById("message").addEventListener("keyup", function (event) {
    if (event.key == "Enter") {
        let message = document.getElementById("message").value;
        socket.emit("new_message", "lobby", message);
        document.getElementById("message").value = "";
    }
})
//顯示訊息-on
showMessage = function(username, message){
    let ul = document.getElementById("chat-messages");
    let li = document.createElement("li");
    li.appendChild(document.createTextNode(`${username}: ${message}`));
    if (username === "system") {
        li.style.color = "#888";
    }
    ul.appendChild(li);
    ul.scrollTop = ul.scrollHeight;
}
socket.on("chat", function(data) {
    console.log(data["username"], data["message"])
    showMessage(data["username"], data["message"])
})