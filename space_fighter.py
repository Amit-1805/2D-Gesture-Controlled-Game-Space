import cv2
import mediapipe as mp
import pygame
import random
import math
import time
import mysql.connector
import subprocess

# ---------- DATABASE ----------
def db_connect():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # your mysql password
        database="game_login"
    )

def get_username(user_id):
    try:
        db = db_connect()
        cur = db.cursor()
        cur.execute("SELECT username FROM users WHERE id=%s", (user_id,))
        result = cur.fetchone()
        cur.close()
        db.close()
        return result[0] if result else "Player"
    except:
        return "Player"

def update_game_stats(user_id, score, play_time):
    try:
        db = db_connect()
        cur = db.cursor()

        cur.execute("""
            SELECT high_score, total_time, total_plays
            FROM game_stats
            WHERE user_id=%s AND game_name=%s
        """, (user_id, "Gesture Space Shooter"))

        result = cur.fetchone()

        if result:
            old_high, old_time, old_plays = result
            new_high = max(old_high, score)
            new_total_time = old_time + play_time
            new_total_plays = old_plays + 1
            new_avg_time = new_total_time / new_total_plays

            cur.execute("""
                UPDATE game_stats
                SET high_score=%s,
                    total_time=%s,
                    total_plays=%s,
                    avg_time=%s
                WHERE user_id=%s AND game_name=%s
            """, (
                new_high,
                new_total_time,
                new_total_plays,
                new_avg_time,
                user_id,
                "Gesture Space Shooter"
            ))
        else:
            cur.execute("""
                INSERT INTO game_stats
                (user_id, game_name, high_score, total_time, total_plays, avg_time)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (
                user_id,
                "Gesture Space Shooter",
                score,
                play_time,
                1,
                play_time
            ))

        db.commit()
        cur.close()
        db.close()

    except Exception as e:
        print("DB ERROR:", e)


# ---------- GET SESSION ----------
with open("session.txt", "r") as f:
    user_id = int(f.read())

username = get_username(user_id)


# ---------- GAME FUNCTION ----------
def run_game():

    pygame.init()
    WIDTH, HEIGHT = 900, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Gesture Space Shooter")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Segoe UI", 26)
    big_font = pygame.font.SysFont("Segoe UI", 60)

    # Load Images
    SHIP_IMG = pygame.image.load("images/ship.png").convert_alpha()
    SHIP_IMG = pygame.transform.scale(SHIP_IMG, (120, 130))

    BULLET_IMG = pygame.image.load("images/bullet.png").convert_alpha()
    BULLET_IMG = pygame.transform.scale(BULLET_IMG, (70, 70))

    ENEMY_IMG = pygame.image.load("images/enemy.png").convert_alpha()
    ENEMY_IMG = pygame.transform.scale(ENEMY_IMG, (70, 70))

    BG_IMG = pygame.image.load("images/bg.png").convert()
    BG_IMG = pygame.transform.scale(BG_IMG, (WIDTH, HEIGHT))

    WHITE = (240, 240, 240)

    ship_x = WIDTH // 2
    ship_y = HEIGHT - 80
    smooth_x = ship_x

    bullets = []
    bullet_speed = 8

    enemies = []
    enemy_speed = 2
    enemies_per_wave = 1

    last_enemy_wave = time.time()
    last_difficulty = time.time()

    score = 0
    lives = 3

    start_time = time.time()
    stats_saved = False

    # Mediapipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1)
    mp_draw = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)

    def spawn_enemy():
        return {"x": random.randint(40, WIDTH - 40), "y": -40}

    def is_pinch(hand):
        thumb = hand.landmark[4]
        index = hand.landmark[8]
        dist = math.hypot(thumb.x - index.x, thumb.y - index.y)
        return dist < 0.04

    def draw_button(text, x, y, w, h):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        rect = pygame.Rect(x, y, w, h)

        if rect.collidepoint(mouse):
            pygame.draw.rect(screen, (100, 200, 255), rect, border_radius=10)
            if click[0] == 1:
                return True
        else:
            pygame.draw.rect(screen, (70, 130, 180), rect, border_radius=10)

        txt = font.render(text, True, WHITE)
        screen.blit(txt, (x + w//2 - txt.get_width()//2,
                          y + h//2 - txt.get_height()//2))
        return False

    running = True
    game_over = False

    while running:
        screen.blit(BG_IMG, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game_over:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            pinch = False

            if result.multi_hand_landmarks:
                for hand in result.multi_hand_landmarks:
                    index = hand.landmark[8]
                    ship_x = int(index.x * WIDTH)
                    pinch = is_pinch(hand)
                    mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

            smooth_x += (ship_x - smooth_x) * 0.25
            ship_x = max(0, min(WIDTH - 60, int(smooth_x)))

            if pinch and len(bullets) < 6:
                bullets.append({"x": ship_x + 30, "y": ship_y})

            for bullet in bullets[:]:
                bullet["y"] -= bullet_speed
                screen.blit(BULLET_IMG, (bullet["x"], bullet["y"]))
                if bullet["y"] < 0:
                    bullets.remove(bullet)

            if time.time() - last_enemy_wave >= 3:
                for _ in range(enemies_per_wave):
                    enemies.append(spawn_enemy())
                last_enemy_wave = time.time()

            if time.time() - last_difficulty >= 5:
                enemies_per_wave += 1
                enemy_speed += 0.3
                last_difficulty = time.time()

            for enemy in enemies[:]:
                enemy["y"] += enemy_speed
                screen.blit(ENEMY_IMG, (enemy["x"] - 28, enemy["y"] - 28))

                for bullet in bullets[:]:
                    if math.hypot(enemy["x"] - bullet["x"], enemy["y"] - bullet["y"]) < 28:
                        score += 1
                        enemies.remove(enemy)
                        bullets.remove(bullet)
                        break

                if enemy["y"] > HEIGHT:
                    enemies.remove(enemy)
                    lives -= 1
                    if lives <= 0:
                        game_over = True

            screen.blit(SHIP_IMG, (ship_x, ship_y))

            # HUD
            screen.blit(font.render(f"Player: {username}", True, WHITE), (20, 20))
            screen.blit(font.render(f"Score: {score}", True, WHITE), (20, 50))
            screen.blit(font.render(f"Lives: {lives}", True, WHITE), (20, 80))

            cv2.imshow("Hand Tracking", frame)

        else:
            over = big_font.render("GAME OVER", True, WHITE)
            final = font.render(f"{username}'s Score: {score}", True, WHITE)

            screen.blit(over, (WIDTH//2 - 180, HEIGHT//2 - 100))
            screen.blit(final, (WIDTH//2 - 120, HEIGHT//2 - 40))

            if not stats_saved:
                play_time = time.time() - start_time
                update_game_stats(user_id, score, play_time)
                stats_saved = True

            if draw_button("Restart", WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50):
                cap.release()
                cv2.destroyAllWindows()
                run_game()
                return

            if draw_button("Main Menu", WIDTH//2 - 100, HEIGHT//2 + 90, 200, 50):
                cap.release()
                cv2.destroyAllWindows()
                pygame.quit()
                subprocess.Popen(["python", "main.py"])
                return

        pygame.display.update()
        clock.tick(60)

        if cv2.waitKey(1) & 0xFF == 27:
            running = False

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()


# ---------- SAFE EXECUTION ----------
if __name__ == "__main__":
    run_game()