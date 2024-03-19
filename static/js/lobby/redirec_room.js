// 创建房间
function createRoom() {
    const roomName = document.getElementById('createRoomName').value;
    const roomPassword = document.getElementById('createRoomPassword').value;
    const passwordCheckbox = document.getElementById('createPasswordCheckbox').checked;
    
    localStorage.setItem('roomPassword', roomPassword);

    socket.emit("create_room", roomName, roomPassword, username);
    socket.on("create_room_response", function(response) {
        if (response.accept === true) {
            console.log(response.roomhash)
            const roomHash = response.roomhash
            localStorage.setItem('roomHash', roomHash);
            const newUrl = `${applicationRoot}/rooms/${roomName}?username=${username}`;
            window.location.href = newUrl;
        } else {
            console.error('Error:', error);
            alert('出现错误，请稍后重试！');
        }
    })
}

// 加入房间按钮点击事件处理函数
function joinRoom() {
    const roomName = document.getElementById('roomNameSpan').innerText;
    const roomHash = document.getElementById('roomHashSpan').innerText;
    const roomPassword = document.getElementById('roomPasswordInput').value;
    socket.emit("knock_room", roomHash, roomPassword);
    socket.on("knock_room_response", function(response) {
        if (response.accept === true) {
            localStorage.setItem('roomHash', roomHash);
            localStorage.setItem('roomPassword', roomPassword);
            newUrl = `${applicationRoot}/rooms/${roomName}?username=${username}`
            window.location.href = newUrl;
        } else {
            if (response.message) {
                document.getElementById('errorMessage').textContent = response.message
                document.getElementById('errorMessageRow').style.color = 'red';
                document.getElementById('errorMessageRow').style.display = 'block';
            }
        }

    })


}