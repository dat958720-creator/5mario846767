import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Mario Challenge - 60s",
    page_icon="🍄",
    layout="centered"
)

st.title("🍄 Mario Speed Run - 60 Giây")

# Lựa chọn độ khó từ Streamlit UI
difficulty = st.selectbox(
    "🎯 Chọn độ khó:",
    ["Dễ (Easy)", "Trung bình (Medium)", "Khó (Hard)"],
    index=1
)

# Ánh xạ thông số độ khó
diff_params = {
    "Dễ (Easy)": {"speed": 5, "coin_size": 12, "has_enemy": False, "enemy_speed": 0},
    "Trung bình (Medium)": {"speed": 4, "coin_size": 10, "has_enemy": False, "enemy_speed": 0},
    "Khó (Hard)": {"speed": 3.5, "coin_size": 8, "has_enemy": True, "enemy_speed": 2}
}

current_param = diff_params[difficulty]

st.markdown("""
**Hướng dẫn:**
* **Di chuyển:** `A / D` hoặc `Mũi tên Trái / Phải`
* **Nhảy:** `W / Space` hoặc `Mũi tên Lên`
* **Mục tiêu:** Nhặt nhiều đồng xu nhất có thể trong **60 giây**! (Tránh Goomba màu nâu ở chế độ Khó)
""")

# Mã HTML/JS Game
mario_game_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: #5c94fc;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: Arial, sans-serif;
        }}
        canvas {{
            background: #5c94fc;
            border: 4px solid #000;
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="600" height="340"></canvas>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        // --- Cấu hình Web Audio API (Tạo âm thanh dạng Synthesizer) ---
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

        function playSound(type) {{
            if (audioCtx.state === 'suspended') {{
                audioCtx.resume();
            }}
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);

            const now = audioCtx.currentTime;

            if (type === 'jump') {{
                osc.type = 'sine';
                osc.frequency.setValueAtTime(150, now);
                osc.frequency.exponentialRampToValueAtTime(400, now + 0.15);
                gain.gain.setValueAtTime(0.3, now);
                gain.gain.linearRampToValueAtTime(0.01, now + 0.15);
                osc.start(now);
                osc.stop(now + 0.15);
            }} else if (type === 'coin') {{
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(987.77, now); // B5
                osc.frequency.setValueAtTime(1318.51, now + 0.08); // E6
                gain.gain.setValueAtTime(0.3, now);
                gain.gain.linearRampToValueAtTime(0.01, now + 0.25);
                osc.start(now);
                osc.stop(now + 0.25);
            }} else if (type === 'hit') {{
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(120, now);
                osc.frequency.linearRampToValueAtTime(40, now + 0.2);
                gain.gain.setValueAtTime(0.4, now);
                gain.gain.linearRampToValueAtTime(0.01, now + 0.2);
                osc.start(now);
                osc.stop(now + 0.2);
            }} else if (type === 'gameover') {{
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(300, now);
                osc.frequency.linearRampToValueAtTime(100, now + 0.6);
                gain.gain.setValueAtTime(0.4, now);
                gain.gain.linearRampToValueAtTime(0.01, now + 0.6);
                osc.start(now);
                osc.stop(now + 0.6);
            }}
        }}

        // --- Cấu hình Game ---
        const config = {{
            speed: {current_param['speed']},
            coinRadius: {current_param['coin_size']},
            hasEnemy: {str(current_param['has_enemy']).lower()},
            enemySpeed: {current_param['enemy_speed']}
        }};

        // Mario
        const mario = {{
            x: 50,
            y: 200,
            width: 30,
            height: 40,
            color: "#e52521",
            vx: 0,
            vy: 0,
            speed: config.speed,
            jumpStrength: -12,
            grounded: false
        }};

        const gravity = 0.6;
        const groundY = 280;

        // Đồng xu
        let coin = {{ x: 300, y: 200, radius: config.coinRadius, collected: false }};
        let score = 0;

        // Kẻ địch (Goomba)
        let enemy = {{
            x: 450,
            y: groundY - 25,
            width: 25,
            height: 25,
            dx: config.enemySpeed,
            color: "#795548"
        }};

        // Thời gian
        let timeLeft = 60;
        let gameOver = false;

        // Đếm ngược thời gian
        const timerInterval = setInterval(() => {{
            if (!gameOver) {{
                timeLeft--;
                if (timeLeft <= 0) {{
                    timeLeft = 0;
                    gameOver = true;
                    playSound('gameover');
                    clearInterval(timerInterval);
                }}
            }}
        }}, 1000);

        // Bàn phím
        const keys = {{}};
        window.addEventListener("keydown", e => {{ 
            keys[e.code] = true;
            if (audioCtx.state === 'suspended') audioCtx.resume();
        }});
        window.addEventListener("keyup", e => {{ keys[e.code] = false; }});

        function resetGame() {{
            score = 0;
            timeLeft = 60;
            gameOver = false;
            mario.x = 50;
            mario.y = 200;
            mario.vy = 0;
            mario.vx = 0;
            coin.x = 300;
            coin.y = 200;
            coin.collected = false;
        }}

        function update() {{
            if (gameOver) return;

            // Di chuyển
            if (keys["ArrowRight"] || keys["KeyD"]) mario.vx = mario.speed;
            else if (keys["ArrowLeft"] || keys["KeyA"]) mario.vx = -mario.speed;
            else mario.vx = 0;

            // Nhảy
            if ((keys["ArrowUp"] || keys["Space"] || keys["KeyW"]) && mario.grounded) {{
                mario.vy = mario.jumpStrength;
                mario.grounded = false;
                playSound('jump');
            }}

            // Trọng lực & vị trí
            mario.vy += gravity;
            mario.x += mario.vx;
            mario.y += mario.vy;

            // Biên màn hình
            if (mario.x < 0) mario.x = 0;
            if (mario.x + mario.width > canvas.width) mario.x = canvas.width - mario.width;

            // Va chạm đất
            if (mario.y + mario.height >= groundY) {{
                mario.y = groundY - mario.height;
                mario.vy = 0;
                mario.grounded = true;
            }}

            // Di chuyển Goomba
            if (config.hasEnemy) {{
                enemy.x += enemy.dx;
                if (enemy.x <= 100 || enemy.x + enemy.width >= canvas.width - 20) {{
                    enemy.dx *= -1;
                }}

                // Va chạm Goomba (Trừ điểm)
                if (mario.x < enemy.x + enemy.width &&
                    mario.x + mario.width > enemy.x &&
                    mario.y < enemy.y + enemy.height &&
                    mario.y + mario.height > enemy.y) {{
                    
                    score = Math.max(0, score - 5);
                    playSound('hit');
                    // Đẩy Mario lùi lại khi va chạm
                    mario.x -= 30;
                    mario.vy = -6;
                }}
            }}

            // Ăn xu
            if (!coin.collected &&
                mario.x < coin.x + coin.radius &&
                mario.x + mario.width > coin.x - coin.radius &&
                mario.y < coin.y + coin.radius &&
                mario.y + mario.height > coin.y - coin.radius) {{
                
                coin.collected = true;
                score += 10;
                playSound('coin');
                
                setTimeout(() => {{
                    coin.x = Math.random() * (canvas.width - 100) + 50;
                    coin.y = Math.random() * (groundY - 120) + 100;
                    coin.collected = false;
                }}, 400);
            }}
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Mặt đất
            ctx.fillStyle = "#c84c0c";
            ctx.fillRect(0, groundY, canvas.width, canvas.height - groundY);
            ctx.fillStyle = "#fcb42c";
            ctx.fillRect(0, groundY, canvas.width, 6);

            // Goomba (nếu chế độ Khó)
            if (config.hasEnemy) {{
                ctx.fillStyle = enemy.color;
                ctx.fillRect(enemy.x, enemy.y, enemy.width, enemy.height);
                // Mắt enemy
                ctx.fillStyle = "#FFF";
                ctx.fillRect(enemy.x + 3, enemy.y + 5, 5, 5);
                ctx.fillRect(enemy.x + 15, enemy.y + 5, 5, 5);
            }}

            // Mario
            ctx.fillStyle = mario.color;
            ctx.fillRect(mario.x, mario.y, mario.width, mario.height);
            // Mũ
            ctx.fillStyle = "#e52521";
            ctx.fillRect(mario.x - 2, mario.y, mario.width + 4, 8);
            // Quần
            ctx.fillStyle = "#0000fc";
            ctx.fillRect(mario.x + 4, mario.y + 20, mario.width - 8, 15);

            // Đồng xu
            if (!coin.collected) {{
                ctx.beginPath();
                ctx.arc(coin.x, coin.y, coin.radius, 0, Math.PI * 2);
                ctx.fillStyle = "#f8d800";
                ctx.fill();
                ctx.lineWidth = 2;
                ctx.strokeStyle = "#000";
                ctx.stroke();
                ctx.closePath();
            }}

            // HUD (Điểm + Thời gian)
            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 18px Arial";
            ctx.fillText("SCORE: " + score, 20, 30);
            
            // Đổi màu thời gian khi gần hết giờ
            ctx.fillStyle = timeLeft <= 10 ? "#ff2222" : "#ffffff";
            ctx.fillText("TIME: " + timeLeft + "s", canvas.width - 120, 30);

            // Màn hình Game Over
            if (gameOver) {{
                ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 36px Arial";
                ctx.textAlign = "center";
                ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2 - 20);

                ctx.font = "bold 22px Arial";
                ctx.fillStyle = "#f8d800";
                ctx.fillText("TỔNG ĐIỂM: " + score, canvas.width / 2, canvas.height / 2 + 20);

                ctx.font = "16px Arial";
                ctx.fillStyle = "#ffffff";
                ctx.fillText("F5 hoặc thay đổi độ khó để chơi lại!", canvas.width / 2, canvas.height / 2 + 60);
                ctx.textAlign = "start";
            }}
        }}

        function gameLoop() {{
            update();
            draw();
            requestAnimationFrame(gameLoop);
        }}

        gameLoop();
    </script>
</body>
</html>
"""

# Hiển thị game
components.html(mario_game_html, height=380)
