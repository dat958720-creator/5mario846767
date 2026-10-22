import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Mario & Friends Challenge",
    page_icon="🍄",
    layout="centered"
)

# Khởi tạo từ điển cấu hình độ khó chung để dùng cho cả 2 màn hình
diff_params = {
    "Dễ (Easy)": {"speed": 5, "coin_size": 12, "has_enemy": False, "enemy_speed": 0},
    "Trung bình (Medium)": {"speed": 4, "coin_size": 10, "has_enemy": False, "enemy_speed": 0},
    "Khó (Hard - Có Goomba)": {"speed": 3.5, "coin_size": 8, "has_enemy": True, "enemy_speed": 2}
}

char_colors = {
    "Mario (Đỏ)": "#e52521",
    "Luigi (Xanh lá)": "#4caf50",
    "Peach (Hồng)": "#ff4081",
    "Toad (Xanh dương)": "#00bcd4"
}

# Khởi tạo trạng thái game trong session_state
if "game_started" not in st.session_state:
    st.session_state.game_started = False

# --- MÀN HÌNH HOME (Chọn nhân vật & độ khó) ---
if not st.session_state.game_started:
    st.title("🍄 Màn Hình Chính - Mario Challenge")
    st.write("Hãy chọn nhân vật và độ khó trước khi bước vào thử thách 60 giây!")

    col1, col2 = st.columns(2)

    with col1:
        character = st.selectbox(
            "👤 Chọn Nhân vật:",
            list(char_colors.keys())
        )

    with col2:
        difficulty = st.selectbox(
            "🎯 Chọn Độ khó:",
            list(diff_params.keys())
        )

    selected_color = char_colors[character]
    current_param = diff_params[difficulty]

    st.markdown("---")
    if st.button("🚀 BẮT ĐẦU CHƠI", type="primary", use_container_width=True):
        st.session_state.game_started = True
        st.session_state.character = character
        st.session_state.difficulty_name = difficulty
        st.session_state.color = selected_color
        st.session_state.param = current_param
        st.rerun()

# --- MÀN HÌNH CHƠI GAME ---
else:
    char_name = st.session_state.character
    diff_name = st.session_state.difficulty_name
    char_color = st.session_state.color
    param = st.session_state.param

    # Header hiển thị thông tin và nút quay lại Home
    col_info, col_btn = st.columns([3, 1])
    with col_info:
        st.subheader(f"🎮 Nhân vật: {char_name} | Độ khó: {diff_name}")
    with col_btn:
        if st.button("🏠 Về Trang Chủ"):
            st.session_state.game_started = False
            st.rerun()

    st.write("Dùng phím **A/D** hoặc **Mũi tên Trái/Phải** để di chuyển, **W/Space** để nhảy. Nhặt thật nhiều đồng xu trong **60 giây**!")

    # Mã HTML/JS Nhúng Game
    game_html = f"""
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

            // --- Web Audio API (Âm thanh) ---
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            function playSound(type) {{
                if (audioCtx.state === 'suspended') audioCtx.resume();
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
                    osc.start(now); osc.stop(now + 0.15);
                }} else if (type === 'coin') {{
                    osc.type = 'triangle';
                    osc.frequency.setValueAtTime(987.77, now);
                    osc.frequency.setValueAtTime(1318.51, now + 0.08);
                    gain.gain.setValueAtTime(0.3, now);
                    gain.gain.linearRampToValueAtTime(0.01, now + 0.25);
                    osc.start(now); osc.stop(now + 0.25);
                }} else if (type === 'hit') {{
                    osc.type = 'sawtooth';
                    osc.frequency.setValueAtTime(120, now);
                    osc.frequency.linearRampToValueAtTime(40, now + 0.2);
                    gain.gain.setValueAtTime(0.4, now);
                    gain.gain.linearRampToValueAtTime(0.01, now + 0.2);
                    osc.start(now); osc.stop(now + 0.2);
                }} else if (type === 'gameover') {{
                    osc.type = 'sawtooth';
                    osc.frequency.setValueAtTime(300, now);
                    osc.frequency.linearRampToValueAtTime(100, now + 0.6);
                    gain.gain.setValueAtTime(0.4, now);
                    gain.gain.linearRampToValueAtTime(0.01, now + 0.6);
                    osc.start(now); osc.stop(now + 0.6);
                }}
            }}

            const config = {{
                speed: {param['speed']},
                coinRadius: {param['coin_size']},
                hasEnemy: {str(param['has_enemy']).lower()},
                enemySpeed: {param['enemy_speed']},
                color: "{char_color}"
            }};

            const player = {{
                x: 50, y: 200, width: 30, height: 40,
                color: config.color,
                vx: 0, vy: 0, speed: config.speed,
                jumpStrength: -12, grounded: false
            }};

            const gravity = 0.6;
            const groundY = 280;

            let coin = {{ x: 300, y: 200, radius: config.coinRadius, collected: false }};
            let score = 0;
            let enemy = {{ x: 450, y: groundY - 25, width: 25, height: 25, dx: config.enemySpeed, color: "#795548" }};

            let timeLeft = 60;
            let gameOver = false;

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

            const keys = {{}};
            window.addEventListener("keydown", e => {{ 
                keys[e.code] = true;
                if (audioCtx.state === 'suspended') audioCtx.resume();
            }});
            window.addEventListener("keyup", e => {{ keys[e.code] = false; }});

            function update() {{
                if (gameOver) return;

                if (keys["ArrowRight"] || keys["KeyD"]) player.vx = player.speed;
                else if (keys["ArrowLeft"] || keys["KeyA"]) player.vx = -player.speed;
                else player.vx = 0;

                if ((keys["ArrowUp"] || keys["Space"] || keys["KeyW"]) && player.grounded) {{
                    player.vy = player.jumpStrength;
                    player.grounded = false;
                    playSound('jump');
                }}

                player.vy += gravity;
                player.x += player.vx;
                player.y += player.vy;

                if (player.x < 0) player.x = 0;
                if (player.x + player.width > canvas.width) player.x = canvas.width - player.width;

                if (player.y + player.height >= groundY) {{
                    player.y = groundY - player.height;
                    player.vy = 0;
                    player.grounded = true;
                }}

                if (config.hasEnemy) {{
                    enemy.x += enemy.dx;
                    if (enemy.x <= 100 || enemy.x + enemy.width >= canvas.width - 20) enemy.dx *= -1;

                    if (player.x < enemy.x + enemy.width && player.x + player.width > enemy.x &&
                        player.y < enemy.y + enemy.height && player.y + player.height > enemy.y) {{
                        score = Math.max(0, score - 5);
                        playSound('hit');
                        player.x -= 30;
                        player.vy = -6;
                    }}
                }}

                if (!coin.collected &&
                    player.x < coin.x + coin.radius && player.x + player.width > coin.x - coin.radius &&
                    player.y < coin.y + coin.radius && player.y + player.height > coin.y - coin.radius) {{
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

                if (config.hasEnemy) {{
                    ctx.fillStyle = enemy.color;
                    ctx.fillRect(enemy.x, enemy.y, enemy.width, enemy.height);
                }}

                // Nhân vật
                ctx.fillStyle = player.color;
                ctx.fillRect(player.x, player.y, player.width, player.height);
                ctx.fillStyle = "#000000";
                ctx.fillRect(player.x + 4, player.y + 20, player.width - 8, 15);

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

                // Điểm & Thời gian
                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 18px Arial";
                ctx.fillText("SCORE: " + score, 20, 30);
                ctx.fillStyle = timeLeft <= 10 ? "#ff2222" : "#ffffff";
                ctx.fillText("TIME: " + timeLeft + "s", canvas.width - 120, 30);

                if (gameOver) {{
                    ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    ctx.fillStyle = "#ffffff";
                    ctx.font = "bold 36px Arial";
                    ctx.textAlign = "center";
                    ctx.fillText("HẾT GIỜ!", canvas.width / 2, canvas.height / 2 - 20);
                    ctx.font = "bold 22px Arial";
                    ctx.fillStyle = "#f8d800";
                    ctx.fillText("TỔNG ĐIỂM: " + score, canvas.width / 2, canvas.height / 2 + 20);
                    ctx.font = "16px Arial";
                    ctx.fillStyle = "#ffffff";
                    ctx.fillText("Bấm nút 'Về Trang Chủ' ở trên để chơi lại!", canvas.width / 2, canvas.height / 2 + 60);
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

    components.html(game_html, height=380)
