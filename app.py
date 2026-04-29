import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Star Catcher Game",
    page_icon="⭐",
    layout="centered",
)

st.title("⭐ Star Catcher")
st.write("Move the basket, catch stars, avoid meteors, and survive for 60 seconds.")

GAME_HTML = r"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <style>
    body {
      margin: 0;
      background: #0f1223;
      font-family: Arial, sans-serif;
      color: white;
      text-align: center;
      overflow: hidden;
    }

    .game-wrapper {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 100%;
    }

    canvas {
      max-width: 100%;
      border-radius: 16px;
      border: 2px solid rgba(255,255,255,0.25);
      box-shadow: 0 12px 35px rgba(0,0,0,0.35);
      background: #0f1223;
      touch-action: none;
    }

    .instructions {
      font-size: 15px;
      color: #cfd6ee;
      margin-top: 10px;
    }

    .button-row {
      display: flex;
      gap: 12px;
      margin-top: 12px;
      justify-content: center;
      flex-wrap: wrap;
    }

    button {
      background: #55aaff;
      color: white;
      border: none;
      padding: 10px 18px;
      border-radius: 999px;
      font-size: 15px;
      cursor: pointer;
      font-weight: 700;
    }

    button:hover {
      filter: brightness(1.1);
    }
  </style>
</head>
<body>
  <div class="game-wrapper">
    <canvas id="gameCanvas" width="800" height="450"></canvas>
    <div class="instructions">
      Desktop: ← / → or A / D &nbsp; | &nbsp; Mobile: tap/hold left or right side
    </div>
    <div class="button-row">
      <button onclick="restartGame()">Restart Game</button>
    </div>
  </div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const WIDTH = 800;
const HEIGHT = 450;
const PLAYER_W = 80;
const PLAYER_H = 24;
const PLAYER_SPEED = 8;
const STAR_RADIUS = 12;
const METEOR_RADIUS = 16;
const GAME_SECONDS = 60;

const colors = {
  bg: "#0f1223",
  white: "#f5f5f5",
  yellow: "#ffde59",
  blue: "#55aaff",
  red: "#ff5555",
  darkRed: "#a02828",
  green: "#62e68c",
  gray: "#96a0b4"
};

let keys = {};
let pointerDown = false;
let pointerX = WIDTH / 2;
let lastTime = 0;
let game;

function clamp(value, low, high) {
  return Math.max(low, Math.min(high, value));
}

function randomBetween(min, max) {
  return min + Math.random() * (max - min);
}

function resetGame() {
  game = {
    playerX: WIDTH / 2 - PLAYER_W / 2,
    objects: [],
    score: 0,
    lives: 3,
    spawnTimer: 0,
    elapsed: 0,
    state: "playing"
  };
}

function restartGame() {
  resetGame();
}

class FallingObject {
  constructor(kind) {
    this.kind = kind;
    this.x = Math.floor(randomBetween(30, WIDTH - 30));
    this.y = -30;
    this.speed = kind === "star" ? randomBetween(2.6, 5.8) : randomBetween(3.8, 7.2);
    this.radius = kind === "star" ? STAR_RADIUS : METEOR_RADIUS;
    this.angle = Math.random() * Math.PI * 2;
  }

  update(dtFactor) {
    this.y += this.speed * dtFactor;
    this.angle += 0.08 * dtFactor;
  }

  draw() {
    if (this.kind === "star") {
      drawStar(this.x, this.y, this.radius, colors.yellow, this.angle);
    } else {
      ctx.beginPath();
      ctx.fillStyle = colors.red;
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
      ctx.fill();

      ctx.beginPath();
      ctx.fillStyle = colors.darkRed;
      ctx.arc(this.x - 5, this.y - 5, 5, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  collidesWith(rect) {
    const closestX = clamp(this.x, rect.x, rect.x + rect.w);
    const closestY = clamp(this.y, rect.y, rect.y + rect.h);
    const dx = this.x - closestX;
    const dy = this.y - closestY;
    return dx * dx + dy * dy < this.radius * this.radius;
  }
}

function drawStar(x, y, radius, color, angle = 0) {
  ctx.beginPath();
  for (let i = 0; i < 10; i++) {
    const r = i % 2 === 0 ? radius : radius * 0.45;
    const a = angle + i * Math.PI / 5;
    const px = x + Math.cos(a) * r;
    const py = y + Math.sin(a) * r;
    if (i === 0) ctx.moveTo(px, py);
    else ctx.lineTo(px, py);
  }
  ctx.closePath();
  ctx.fillStyle = color;
  ctx.fill();
}

function drawBackground() {
  ctx.fillStyle = colors.bg;
  ctx.fillRect(0, 0, WIDTH, HEIGHT);

  for (let i = 0; i < 45; i++) {
    const x = (i * 97) % WIDTH;
    const y = (i * 53 + Math.floor(game.elapsed * (10 + i % 4))) % HEIGHT;
    const brightness = 120 + (i * 23) % 100;
    ctx.fillStyle = `rgb(${brightness}, ${brightness}, ${brightness})`;
    ctx.beginPath();
    ctx.arc(x, y, 1, 0, Math.PI * 2);
    ctx.fill();
  }
}

function drawText(text, x, y, size = 24, color = colors.white, align = "left", bold = false) {
  ctx.font = `${bold ? "bold" : "normal"} ${size}px Arial`;
  ctx.fillStyle = color;
  ctx.textAlign = align;
  ctx.fillText(text, x, y);
}

function drawRoundedRect(x, y, w, h, r, fill, stroke) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
  ctx.fillStyle = fill;
  ctx.fill();
  if (stroke) {
    ctx.strokeStyle = stroke;
    ctx.lineWidth = 2;
    ctx.stroke();
  }
}

function updateGame(deltaMs) {
  const dtFactor = deltaMs / 16.67;

  if (game.state !== "playing") return;

  game.elapsed += deltaMs / 1000;
  const secondsLeft = Math.max(0, Math.ceil(GAME_SECONDS - game.elapsed));

  if (keys["ArrowLeft"] || keys["a"] || keys["A"]) game.playerX -= PLAYER_SPEED * dtFactor;
  if (keys["ArrowRight"] || keys["d"] || keys["D"]) game.playerX += PLAYER_SPEED * dtFactor;

  if (pointerDown) {
    if (pointerX < WIDTH / 2) game.playerX -= PLAYER_SPEED * dtFactor;
    else game.playerX += PLAYER_SPEED * dtFactor;
  }

  game.playerX = clamp(game.playerX, 0, WIDTH - PLAYER_W);

  game.spawnTimer += deltaMs;
  const spawnDelay = Math.max(430, 900 - game.score * 8);
  if (game.spawnTimer > spawnDelay) {
    const kind = Math.random() < 0.28 ? "meteor" : "star";
    game.objects.push(new FallingObject(kind));
    game.spawnTimer = 0;
  }

  const playerRect = { x: game.playerX, y: HEIGHT - 55, w: PLAYER_W, h: PLAYER_H };

  for (let i = game.objects.length - 1; i >= 0; i--) {
    const obj = game.objects[i];
    obj.update(dtFactor);

    if (obj.collidesWith(playerRect)) {
      if (obj.kind === "star") game.score += 1;
      else game.lives -= 1;
      game.objects.splice(i, 1);
    } else if (obj.y > HEIGHT + 40) {
      game.objects.splice(i, 1);
    }
  }

  if (game.lives <= 0) game.state = "lost";
  if (secondsLeft <= 0) game.state = "won";
}

function drawGame() {
  drawBackground();

  for (const obj of game.objects) obj.draw();

  drawRoundedRect(game.playerX, HEIGHT - 55, PLAYER_W, PLAYER_H, 10, colors.blue, colors.white);

  const secondsLeft = Math.max(0, Math.ceil(GAME_SECONDS - game.elapsed));
  drawText(`Score: ${game.score}`, 16, 34, 24);
  drawText(`Lives: ${game.lives}`, 16, 64, 24);
  drawText(`Time: ${secondsLeft}s`, WIDTH - 130, 34, 24);
  drawText("Catch stars. Avoid meteors.", WIDTH / 2, 34, 18, colors.gray, "center");

  if (game.state === "won" || game.state === "lost") {
    ctx.fillStyle = "rgba(0, 0, 0, 0.68)";
    ctx.fillRect(0, 0, WIDTH, HEIGHT);

    const title = game.state === "won" ? "You Win!" : "Game Over";
    const titleColor = game.state === "won" ? colors.green : colors.red;
    drawText(title, WIDTH / 2, HEIGHT / 2 - 60, 52, titleColor, "center", true);
    drawText(`Final Score: ${game.score}`, WIDTH / 2, HEIGHT / 2, 24, colors.white, "center");
    drawText("Press SPACE, click, or tap Restart Game", WIDTH / 2, HEIGHT / 2 + 45, 24, colors.white, "center");
  }
}

function gameLoop(timestamp) {
  if (!lastTime) lastTime = timestamp;
  const deltaMs = Math.min(33, timestamp - lastTime);
  lastTime = timestamp;

  updateGame(deltaMs);
  drawGame();
  requestAnimationFrame(gameLoop);
}

function getCanvasX(event) {
  const rect = canvas.getBoundingClientRect();
  const clientX = event.touches ? event.touches[0].clientX : event.clientX;
  return ((clientX - rect.left) / rect.width) * WIDTH;
}

window.addEventListener("keydown", (event) => {
  keys[event.key] = true;
  if (game.state !== "playing" && event.code === "Space") restartGame();
});

window.addEventListener("keyup", (event) => {
  keys[event.key] = false;
});

canvas.addEventListener("mousedown", (event) => {
  if (game.state !== "playing") restartGame();
  pointerDown = true;
  pointerX = getCanvasX(event);
});

canvas.addEventListener("mousemove", (event) => {
  if (pointerDown) pointerX = getCanvasX(event);
});

window.addEventListener("mouseup", () => {
  pointerDown = false;
});

canvas.addEventListener("touchstart", (event) => {
  event.preventDefault();
  if (game.state !== "playing") restartGame();
  pointerDown = true;
  pointerX = getCanvasX(event);
});

canvas.addEventListener("touchmove", (event) => {
  event.preventDefault();
  pointerX = getCanvasX(event);
});

canvas.addEventListener("touchend", (event) => {
  event.preventDefault();
  pointerDown = false;
});

resetGame();
requestAnimationFrame(gameLoop);
</script>
</body>
</html>
"""

components.html(GAME_HTML, height=560, scrolling=False)

with st.expander("How to play"):
    st.markdown(
        """
        - Use **Left/Right arrows** or **A/D** to move.
        - On mobile, **tap and hold** the left or right side of the game.
        - Catch yellow stars to increase your score.
        - Avoid red meteors because they reduce lives.
        - Survive for 60 seconds.
        """
    )

st.caption("Built for Streamlit Community Cloud. This version uses an embedded HTML5 canvas game so it works directly in the browser.")
