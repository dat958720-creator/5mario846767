import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang
st.set_page_config(
    page_title="Mario Streamlit Game",
    page_icon="🍄",
    layout="centered"
)

st.title("🍄 Game Mario Mini trên Streamlit")
st.markdown("""
**Hướng dẫn chơi:**
* **Di chuyển:** Phím **A / D** hoặc **Mũi tên Trái / Phải**
* **Nhảy:** Phím **W**, **Space** hoặc **Mũi tên Lên**
""")

# Mã HTML/CSS/JavaScript cho game Mario
mario_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #5c94fc;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: sans-serif;
        }
        canvas {
            background: #5c94fc;
            border: 4px solid #000;
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="600" height="320"></canvas>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        // Trạng thái nhân vật Mario
        const mario = {
            x: 50,
            y: 200,
            width: 30,
            height: 40,
            color: "#e52521",
            vx: 0,
            vy: 0,
            speed: 4,
            jumpStrength: -12,
            grounded: false
        };

        const gravity = 0.6;
        const groundY = 260;

        // Đồng xu
        let coin = { x: 300, y: 190, radius: 10, collected: false };
        let score = 0;

        // Xử lý sự kiện bàn phím
        const keys = {};
        window.addEventListener("keydown", e => { keys[e.code] = true; });
        window.addEventListener("keyup", e => { keys[e.code] = false; });

        function update() {
            // Di chuyển ngang
            if (keys["ArrowRight"] || keys["KeyD"]) mario.vx = mario.speed;
            else if (keys["ArrowLeft"] || keys["KeyA"]) mario.vx = -mario.speed;
            else mario.vx = 0;

            // Nhảy
            if ((keys["ArrowUp"] || keys["Space"] || keys["KeyW"]) && mario.grounded) {
                mario.vy = mario.jumpStrength;
                mario.grounded = false;
            }

            // Trọng lực
            mario.vy += gravity;

            // Cập nhật vị trí
            mario.x += mario.vx;
            mario.y += mario.vy;

            // Giới hạn biên màn hình
            if (mario.x < 0) mario.x = 0;
            if (mario.x + mario.width > canvas.width) mario.x = canvas.width - mario.width;

            // Va chạm mặt đất
            if (mario.y + mario.height >= groundY) {
                mario.y = groundY - mario.height;
                mario.vy = 0;
                mario.grounded = true;
            }

            // Ăn đồng xu
            if (!coin.collected &&
                mario.x < coin.x + coin.radius &&
                mario.x + mario.width > coin.x - coin.radius &&
                mario.y < coin.y + coin.radius &&
                mario.y + mario.height > coin.y - coin.radius) {
                
                coin.collected = true;
                score += 10;
                
                // Tạo đồng xu mới ngẫu nhiên
                setTimeout(() => {
                    coin.x = Math.random() * (canvas.width - 80) + 40;
                    coin.y = Math.random() * (groundY - 100) + 100;
                    coin.collected = false;
                }, 600);
            }
        }

        function draw() {
            // Xóa khung hình cũ
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Vẽ mặt đất
            ctx.fillStyle = "#c84c0c";
            ctx.fillRect(0, groundY, canvas.width, canvas.height - groundY);
            ctx.fillStyle = "#fcb42c";
            ctx.fillRect(0, groundY, canvas.width, 6);

            // Vẽ Mario
            ctx.fillStyle = mario.color;
            ctx.fillRect(mario.x, mario.y, mario.width, mario.height);
            // Mũ Mario
            ctx.fillStyle = "#e52521";
            ctx.fillRect(mario.x - 2, mario.y, mario.width + 4, 8);
            // Quần yếm
            ctx.fillStyle = "#0000fc";
            ctx.fillRect(mario.x + 4, mario.y + 20, mario.width - 8, 15);

            // Vẽ đồng xu
            if (!coin.collected) {
                ctx.beginPath();
                ctx.arc(coin.x, coin.y, coin.radius, 0, Math.PI * 2);
                ctx.fillStyle = "#f8d800";
                ctx.fill();
                ctx.lineWidth = 2;
                ctx.strokeStyle = "#000";
                ctx.stroke();
                ctx.closePath();
            }

            // Bảng điểm
            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 20px Arial";
            ctx.fillText("SCORE: " + score, 20, 35);
        }

        function gameLoop() {
            update();
            draw();
            requestAnimationFrame(gameLoop);
        }

        gameLoop();
    </script>
</body>
</html>
"""

# Nhúng Game vào giao diện Streamlit
components.html(mario_html, height=360)
