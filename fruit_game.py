import cv2
import mediapipe as mp
import pygame
import random
import time
import mysql.connector
import subprocess
import sys
import os

# ---------- DATABASE ----------
def db_connect():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
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

# ✅ UPDATED FUNCTION (FULL STATS)
def update_game_stats(user_id, score, play_time):
    try:
        db = db_connect()
        cur = db.cursor()

        cur.execute("""
            SELECT high_score, total_plays, total_time
            FROM game_stats
            WHERE user_id=%s AND game_name=%s
        """, (user_id, "Fruit Catcher"))

        result = cur.fetchone()

        if result:
            old_score, plays, total_time = result

            new_score = max(score, old_score)
            plays += 1
            total_time += play_time
            avg_time = total_time / plays

            cur.execute("""
                UPDATE game_stats
                SET high_score=%s,
                    total_plays=%s,
                    total_time=%s,
                    avg_time=%s
                WHERE user_id=%s AND game_name=%s
            """, (new_score, plays, total_time, avg_time, user_id, "Fruit Catcher"))

        else:
            cur.execute("""
                INSERT INTO game_stats
                (user_id, game_name, high_score, total_plays, total_time, avg_time)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, "Fruit Catcher", score, 1, play_time, play_time))

        db.commit()
        cur.close()
        db.close()

    except Exception as e:
        print("[DB ERROR]", e)


# ---------- GET SESSION ----------
try:
    with open("session.txt", "r") as f:
        user_id = int(f.read())
except:
    print("Session not found!")
    sys.exit()

username = get_username(user_id)


# ---------- MAIN GAME ----------
def run_game():

    pygame.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Gesture Controlled Catcher")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Segoe UI", 32, bold=True)
    big_font = pygame.font.SysFont("Segoe UI", 70, bold=True)

    BLACK = (0, 0, 0)

    bg_image = pygame.image.load("images/backgroundoffruit.png")
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

    basket_img = pygame.image.load("images/basket.png")
    basket_img = pygame.transform.scale(basket_img, (200, 120))

    apple = pygame.image.load("images/apple-removebg-preview.png")
    banana = pygame.image.load("images/pineapple-removebg-preview.png")
    orange = pygame.image.load("images/grephs-removebg-preview.png")

    apple = pygame.transform.scale(apple, (80, 80))
    banana = pygame.transform.scale(banana, (80, 80))
    orange = pygame.transform.scale(orange, (80, 80))

    fruit_images = [apple, banana, orange]

    catcher_width = 200
    catcher_height = 120
    catcher_x = WIDTH // 2
    catcher_y = HEIGHT - 140
    smooth_x = catcher_x

    fruit_img = random.choice(fruit_images)
    fruit_x = random.randint(40, WIDTH - 80)
    fruit_y = 0
    fruit_speed = 4

    score = 0
    lives = 3
    last_speed_increase = time.time()

    # ✅ START TIMER
    game_start_time = time.time()

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1)
    mp_draw = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)

    running = True
    game_over = False
    score_saved = False

    def draw_button(text, x, y, w, h):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        rect = pygame.Rect(x, y, w, h)

        if rect.collidepoint(mouse):
            pygame.draw.rect(screen, (180, 180, 180), rect, border_radius=12)
            if click[0] == 1:
                pygame.time.delay(200)
                return True
        else:
            pygame.draw.rect(screen, (220, 220, 220), rect, border_radius=12)

        txt = font.render(text, True, BLACK)
        screen.blit(txt, (x + w//2 - txt.get_width()//2,
                          y + h//2 - txt.get_height()//2))
        return False

    while running:

        screen.blit(bg_image, (0, 0))

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

            if result.multi_hand_landmarks:
                for hand in result.multi_hand_landmarks:
                    index_finger = hand.landmark[8]
                    catcher_x = int(index_finger.x * WIDTH) - catcher_width // 2
                    mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

            smooth_x += (catcher_x - smooth_x) * 0.2
            catcher_x = max(0, min(WIDTH - catcher_width, int(smooth_x)))

            fruit_y += fruit_speed

            if (catcher_y < fruit_y + 80 and
                catcher_x < fruit_x < catcher_x + catcher_width):

                score += 1
                fruit_y = 0
                fruit_x = random.randint(40, WIDTH - 80)
                fruit_img = random.choice(fruit_images)

            if fruit_y > HEIGHT:
                lives -= 1
                fruit_y = 0
                fruit_x = random.randint(40, WIDTH - 80)
                fruit_img = random.choice(fruit_images)

                if lives <= 0:
                    game_over = True

            if time.time() - last_speed_increase >= 3:
                fruit_speed += 0.5
                last_speed_increase = time.time()

            screen.blit(basket_img, (catcher_x, catcher_y))
            screen.blit(fruit_img, (fruit_x, fruit_y))

            screen.blit(font.render(f"Player: {username}", True, BLACK), (20, 20))
            screen.blit(font.render(f"Score: {score}", True, BLACK), (20, 60))
            screen.blit(font.render(f"Lives: {lives}", True, BLACK), (20, 100))

            cv2.imshow("Hand Tracking", frame)

        else:

            screen.blit(big_font.render("GAME OVER", True, BLACK),
                        (WIDTH//2 - 220, HEIGHT//2 - 120))

            screen.blit(font.render(f"{username}'s Score: {score}", True, BLACK),
                        (WIDTH//2 - 160, HEIGHT//2 - 40))

            # ✅ SAVE FULL STATS
            if not score_saved:
                game_time = time.time() - game_start_time
                update_game_stats(user_id, score, game_time)
                score_saved = True

            if draw_button("Restart", WIDTH//2 - 120, HEIGHT//2 + 30, 240, 60):
                cap.release()
                cv2.destroyAllWindows()
                pygame.quit()
                run_game()
                return

            if draw_button("Main Menu", WIDTH//2 - 120, HEIGHT//2 + 110, 240, 60):
                cap.release()
                cv2.destroyAllWindows()
                pygame.quit()
                subprocess.Popen([sys.executable, "main.py"])
                return

        pygame.display.update()
        clock.tick(60)

        if cv2.waitKey(1) & 0xFF == 27:
            running = False

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()


# ---------- START GAME ----------
if __name__ == "__main__":
    run_game()