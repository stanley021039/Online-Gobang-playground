socket.emit("user_join_room", roomHash, roomPassword, username);
socket.on("user_join_room_response", function(response) {
    if (response.accept === true){
        responseChara = response["chara"]
        responseBoard = response["borad_pattern"]
        console.log(response.message);
        userchara = responseChara
        for (let j = 0; j < responseBoard.length; j++) {
            for (let i = 0; i < responseBoard[j].length; i++) {
                if (responseBoard[j][i] === 1) {
                    oneStep(i,j,"black");
                } else if (responseBoard[j][i] === -1){
                    oneStep(i,j,"white");
                }
            }
        }
    } else {
        console.log(response.message);
    }
});

socket.on("online_user_update", function(response) {
    responseBlack = response["black_user"]
    responseWhite = response["white_user"]
    responseObserver = response["observer"]

    if (responseBlack === null) {
        document.getElementById("black-player").textContent  = "等待中...";
        document.getElementById("black-player").style.color = 'red'
        show_ai_btn(document.getElementById("set-black-ai"), "set")
        show_move_btn(document.getElementById("move-black"), "show")
    } else if (responseBlack === "AI_PLAYER") {
        document.getElementById("black-player").textContent = `${responseBlack}`;
        document.getElementById("black-player").style.color = 'black'
        show_ai_btn(document.getElementById("set-black-ai"), "remove")
        show_move_btn(document.getElementById("move-black"), "disabled")
    }  else {
        document.getElementById("black-player").textContent = `${responseBlack}`;
        document.getElementById("black-player").style.color = 'black'
        show_ai_btn(document.getElementById("set-black-ai"), "disabled")
        show_move_btn(document.getElementById("move-black"), "disabled")
    }

    if (responseWhite === null) {
        document.getElementById("white-player").textContent = "等待中...";
        document.getElementById("white-player").style.color = 'red'
        show_ai_btn(document.getElementById("set-white-ai"), "set")
        show_move_btn(document.getElementById("move-white"), "show")
    } else if (responseWhite === "AI_PLAYER") {
        document.getElementById("white-player").textContent = `${responseWhite}`;
        document.getElementById("white-player").style.color = 'black'
        show_ai_btn(document.getElementById("set-white-ai"), "remove")
        show_move_btn(document.getElementById("move-white"), "disabled")
    }  else {
        document.getElementById("white-player").textContent = `${responseWhite}`;
        document.getElementById("white-player").style.color = 'black'
        show_ai_btn(document.getElementById("set-white-ai"), "disabled")
        show_move_btn(document.getElementById("move-white"), "disabled")
    }

    if (userchara !== 'observer') {
        show_move_btn(document.getElementById("move-observer"), "show")
    } else {
        show_move_btn(document.getElementById("move-observer"), "disabled")
    }
    document.getElementById("observer-count").textContent = `${responseObserver}`;
})

show_ai_btn = function(button, state){
    if (state === "disabled"){
        button.disabled = true;
        button.style.backgroundColor = "gray";
    } else if (state === "remove") {
        button.textContent = '移除AI';
        button.disabled = false;
        button.style.backgroundColor = "";
    } else {
        button.textContent = '設置AI';
        button.disabled = false;
        button.style.backgroundColor = "";
    }
}

show_move_btn = function(button, state){
    if (state === "disabled"){
        button.disabled = true;
        button.style.backgroundColor = "gray";
    } else {
        button.disabled = false;
        button.style.backgroundColor = "";
    }
}

set_AI = function(chara){
    socket.emit("set_AI", roomHash, username, userchara, chara);
}

user_move = function(chara){
    socket.emit("user_move", roomHash, username, userchara, chara);
}
socket.on("user_move_response", function(response) {
    if (response.accept === true) {
        console.log(userchara, response.chara, response.accept)
        userchara = response.chara
    }
})

document.getElementById("message").addEventListener("keyup", function (event) {
    if (event.key == "Enter") {
        let message = document.getElementById("message").value;
        socket.emit("new_message", roomHash, message);
        document.getElementById("message").value = "";
    }
})

//顯示訊息-emit
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
    showMessage(data["username"], data["message"])
})

setAI = function(chara){
    if (chara === white){
        
    }
}

exit_room = function(){
    localStorage.setItem('roomHash', null);
    localStorage.setItem('roomPassword', null);

    newUrl = `${applicationRoot}?username=${username}`
    window.location.href = newUrl;
}