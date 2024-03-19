var words = document.querySelector(".words");	
var chess = document.getElementById("chess");
var context = chess.getContext("2d");
var width = context.canvas.width;
var height = context.canvas.height;
var margin = 15
var logo = new Image();
// 繪製格線
drawChessMap = function(width, height, margin){
    context.strokeStyle = "#bfbfbf";
    const w_cell = width / 15
    const h_cell = height / 15
    for (let i=0;i<15;i++) {
        context.beginPath();
        context.moveTo(margin,margin+i*h_cell);
        context.lineTo(width-margin,margin+i*h_cell);
        context.moveTo(margin+i*w_cell,margin);
        context.lineTo(margin+i*w_cell,height-margin);
        context.closePath();
        context.stroke();
    }
}
drawChess = function(width, height, margin){
    fetch(`${applicationRoot}/images?imgname=board.jpg`)
        .then(response => {
            if (response.ok) {
                return response.blob();
            } else {
                throw new Error(response["message"]);
            }
        })
        .then(blob => {
            logo.src = URL.createObjectURL(blob);
            logo.onload = function() {
                context.stroke();
                context.clearRect(0, 0, width, height);
                context.drawImage(logo, 0, 0, width, height);
                console.log('drawImage');
                drawChessMap(width, height, margin);
                console.log('drawChessMap');
            };
        })
        .catch(error => {
            console.error('Error fetching image:', error);
        });
}
drawChess(width, height, margin)
//落子事件
oneStep = function(i,j,chara) {
    context.beginPath();
    context.arc(15 + i*30, 15 + j*30, 13, 0, 2*Math.PI);
    context.closePath();
    var gradient = context.createRadialGradient(15 + i*30 + 4, 15 + j*30 - 2, 13, 15 + i*30 + 2, 15 + j*30 - 2, 0);
    if(chara === 'black') {
        gradient.addColorStop(0,"#0a0a0a");
        gradient.addColorStop(1,"#636766");
    } else {
        gradient.addColorStop(0,"#d1d1d1");
        gradient.addColorStop(1,"#f9f9f9");
    }
    context.fillStyle = gradient;
    context.fill();
}

var chessBoard = [];
var over = false;

var rs = document.getElementById("restart");
rs.onclick = function() {
    socket.emit("restart", roomHash, username, userchara);
}

socket.on("restart", function(){
    console.log("restart");
    console.log(width, height, margin);
    drawChess(width, height, margin);
    over = false;
})

// 用戶點擊-emit
chess.onclick = function (e) {
    if (!over && (userchara === 'black' || userchara === 'white')){
        var x = e.offsetX;
        var y = e.offsetY;
        var i = Math.floor(x / 30);
        var j = Math.floor(y / 30);
        console.log(x, y, i, j)
        socket.emit("get_move", roomHash, username, userchara, [i, j]);
        socket.on("get_move_response", function(response) {
            console.log(response["message"])
        })
    }
}
// 用戶點擊-on
socket.on("someone_move", function(response) {
    responseChara = response["chara"]
    responseMove = response["move"]
    responseBoardState = response["board_state"]
    var i, j
    [i, j] = responseMove
    console.log(`${responseChara} move at ${i}, ${j}!`);
    oneStep(i,j,responseChara);
    if (responseBoardState !== 0) {
        over = true
    }
})