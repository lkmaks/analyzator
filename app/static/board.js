
function div(a, b) {
    return Math.floor(a / b);
}


function min (a, b) {
    if (a < b) {
        return a;
    }
    else {
        return b;
    }
}


class Board {
    constructor(room_id, room_name) {
        this.STEP = 50;
        this.STONE_RADIUS = div(this.STEP, 2) - 1;
        this.LEFT_X = 0;
        this.TOP_Y = 0;
        this.SIZE = 15;
        this.LINE_COLOR = 'black';
        this.BOARD_LINE_WIDTH = 1.5;

        this.CNT = 0;
        this.STACK_POS = [];
        this.ARR_POS = []; //  0: empty, 1: black; 2: white
        for (var i = 0; i < this.SIZE; ++i) {
            this.ARR_POS[i] = [];
            for (var j = 0; j < this.SIZE; ++j) {
                this.ARR_POS[i][j] = 0;
            }
        }
        this.room_id = room_id;
        this.room_name = room_name;
        this.users_in = new Set();

        var rooms_tag = $('#rooms').get(0);

        this.containing_element = document.createElement('div');
        this.containing_element.setAttribute('id', 'room_box_' + this.room_id);
        this.containing_element.setAttribute('class', 'big_table panel panel-default');
        rooms_tag.appendChild(this.containing_element);

        this.upper = document.createElement('div');
        this.upper.setAttribute('id', 'room_lower_box_' + this.room_id);
        this.upper.setAttribute('class', 'upper_container panel panel-default');
        this.containing_element.appendChild(this.upper);

        this.lower = document.createElement('div');
        this.lower.setAttribute('id', 'room_lower_box_' + this.room_id);
        this.lower.setAttribute('class', 'lower_container panel panel-default');
        this.containing_element.appendChild(this.lower);

        this.room_id_p = document.createElement('p');
        this.room_id_p.textContent += 'Room #' + room_id;
        this.room_id_p.setAttribute('style', 'display: inline-block; margin: 5px');
        this.lower.appendChild(this.room_id_p);

        this.room_name_p = document.createElement('p');
        this.room_name_p.textContent += this.room_name;
        this.room_name_p.setAttribute('style', 'display: inline-block; margin: 5px');
        this.lower.appendChild(this.room_name_p);

        this.join_button = document.createElement('a');
        this.join_button.setAttribute('href', '/room?id=' + room_id);
        this.join_button.setAttribute('class', 'btn btn-default');
        this.join_button.textContent += 'join';
        this.lower.appendChild(this.join_button);

        this.delete_button = document.createElement('a');
        this.delete_button.setAttribute('class', 'btn btn-default');
        this.delete_button.setAttribute('style', 'background-color: red');
        this.delete_button.setAttribute('id', 'delete_room_' + room_id);
        this.delete_button.textContent += 'delete';
        this.lower.appendChild(this.delete_button);

        var cte = this.containing_element;

        $('#delete_room_' + room_id).on("click", function(event) {
            console.log('123');
            socket.emit('lobby/delete_room', room_id);
        });

        this.can = document.createElement('canvas');
        this.can.setAttribute('id', 'room_' + this.room_id);
        this.upper.appendChild(this.can);
        this.rescale(min(this.upper.offsetHeight, this.upper.offsetWidth));
        this.can.width = this.STEP * 16;
        this.can.height = this.STEP * 16;

        this.render();
    }

    get_context() {
        var can = document.getElementById('room_' + this.room_id);
        return can.getContext("2d");
    }

    undo() {
        if (this.CNT > 0) {
            var x = this.STACK_POS[this.CNT - 1][0];
            var y = this.STACK_POS[this.CNT - 1][1];
            this.CNT -= 1;
            this.ARR_POS[x][y] = 0;
            this.STACK_POS.pop();
        }
        this.render();
    }

    undo_until(i, j) {
        while (!(this.STACK_POS[this.CNT - 1][0] === i && this.STACK_POS[this.CNT - 1][1] === j)) {
            var x = this.STACK_POS[this.CNT - 1][0];
            var y = this.STACK_POS[this.CNT - 1][1];
            this.CNT -= 1;
            this.ARR_POS[x][y] = 0;
            this.STACK_POS.pop();
        }
        this.render();
    }

    add_stone(i, j) {
        console.log(this.room_id, i, j);
        this.CNT += 1;
        this.ARR_POS[i][j] = this.CNT % 2 + 1;
        this.STACK_POS.push([i, j]);
        this.render();
    }

    add_user(username) {
        this.users_in.add(username);
    }

    remove_user(username) {
        this.users_in.delete(username);
    }

    rescale(h) {
        this.STEP = div(h, 16) - 1;
        this.STONE_RADIUS = div(this.STEP, 2) - 1;
    }

    render() {
        this.draw_empty_board();
        var stone_color = 'black';
        var opp_color = 'white';
        for (var i = 0; i < this.CNT; ++i) {
            var x = this.STACK_POS[i][0];
            var y = this.STACK_POS[i][1];
            this.draw_stone(x, y, stone_color, i + 1, opp_color);
            [stone_color, opp_color] = [opp_color, stone_color];
        }
    }

    draw_empty_board() {
        var ctx = this.get_context();
        var bg_img = document.getElementById("background");

        ctx.drawImage(bg_img, this.LEFT_X, this.TOP_Y, this.STEP * (this.SIZE + 1), this.STEP * (this.SIZE + 1));

        ctx.fillStyle = this.LINE_COLOR;
        for (var i = 0; i < this.SIZE; ++i) {
            ctx.beginPath();
            ctx.moveTo(this.LEFT_X + this.STEP, this.TOP_Y + (i + 1) * this.STEP);
            ctx.lineTo(this.LEFT_X + this.STEP * this.SIZE, this.TOP_Y + (i + 1) * this.STEP);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(this.LEFT_X + (i + 1) * this.STEP, this.TOP_Y + this.STEP);
            ctx.lineTo(this.LEFT_X + (i + 1) * this.STEP, this.TOP_Y + this.STEP * this.SIZE);
            ctx.stroke();
        }
    }

    draw_stone(i, j, color, text, text_color) {
        console.log('DRAW', i, j);
        var ctx = this.get_context();
        const white_stone = document.getElementById("white_stone");
        const black_stone = document.getElementById("black_stone");

        var x = (j + 1) * this.STEP - this.STEP / 2 + this.STEP / 20, y = (i + 1) * this.STEP - this.STEP / 2 + this.STEP / 20;
        var w = this.STEP * 1.01, h = this.STEP * 1.01;

        if (color === 'black') {
            ctx.drawImage(black_stone, x, y, w, h)
        } else {
            ctx.drawImage(white_stone, x, y, w, h)
        }

        var x_text = (j + 1) * this.STEP, y_text = (i + 1) * this.STEP;
        ctx.fillStyle = text_color;
        ctx.font = "12px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(text, x_text, y_text, this.STEP);
    }
}


function create_mes(msg) {
    var obj = new Object();
    obj.mes = msg;
    return obj;
}


