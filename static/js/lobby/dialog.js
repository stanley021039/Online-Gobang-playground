// 显示加入房间对话框
function showJoinDialog(roomName, needPwd, roomHash) {
    document.getElementById('joinOverlay').style.display = 'block';
    document.getElementById('joinOverlay').style.animation = 'fadeIn 0.5s forwards';
    console.log(roomName)
    document.getElementById("roomNameSpan").textContent = roomName;
    document.getElementById('roomHashSpan').textContent = roomHash;
    if (needPwd === 'True') {
        document.getElementById('joinPasswordRow').style.display = 'block';
    } else {
        document.getElementById('joinPasswordRow').style.display = 'none';
    }
}

// 隐藏加入房间对话框
function hideJoinDialog() {
    document.getElementById('joinOverlay').style.animation = 'fadeOut 0.5s forwards';
    setTimeout(() => {
        document.getElementById('joinOverlay').style.display = 'none';
        document.getElementById('errorMessageRow').style.display = 'none';
        document.getElementById('roomPasswordInput').value = null;
        document.getElementById('joinPasswordRow').style.display = 'none';
    }, 500);
}

// 切换密码输入框状态
function toggleCreatePasswordInput() {
    const passwordCheckbox = document.getElementById('createPasswordCheckbox');
    const roomPassword = document.getElementById('createRoomPassword');
    roomPassword.disabled = !passwordCheckbox.checked;
}

// 显示创建房间对话框
function showCreateDialog() {
    document.getElementById('createOverlay').style.display = 'block';
    document.getElementById('createOverlay').style.animation = 'fadeIn 0.5s forwards';
    // document.getElementById('createRoomForm').setAttribute('data-room-id', roomId);
}

// 隐藏创建房间对话框
function hideCreateDialog() {
    document.getElementById('createOverlay').style.animation = 'fadeOut 0.5s forwards';
    setTimeout(() => {
        document.getElementById('createOverlay').style.display = 'none';
        document.getElementById('createRoomForm').reset();
        document.getElementById('createRoomPassword').disabled = true;
    }, 500);
}