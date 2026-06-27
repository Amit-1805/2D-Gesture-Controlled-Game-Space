import pygame
import sys
import mysql.connector
import subprocess

# ---------- INIT ----------
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Login")
clock = pygame.time.Clock()

# ---------- COLORS ----------
BG = (25, 35, 55)
WHITE = (240, 240, 240)
RED = (220, 80, 80)
GRAY = (180, 180, 180)
GREEN = (80, 200, 120)
BLUE = (100, 160, 255)

# ---------- FONTS ----------
font = pygame.font.SysFont("Segoe UI", 26)
title_font = pygame.font.SysFont("Segoe UI", 46, bold=True)

# ---------- INPUT BOX ----------
class InputBox:
    def __init__(self, x, y, w, h, hidden=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.active = False
        self.hidden = hidden

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key != pygame.K_RETURN:
                self.text += event.unicode

    def draw(self):
        pygame.draw.rect(screen, WHITE if self.active else GRAY, self.rect, 2)
        show_text = "*" * len(self.text) if self.hidden else self.text
        txt_surface = font.render(show_text, True, WHITE)
        screen.blit(txt_surface, (self.rect.x + 10, self.rect.y + 8))


# ---------- DATABASE ----------
def db_connect():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",   # <-- Put your MySQL password
        database="game_login"
    )


def check_login(username, password):
    try:
        db = db_connect()
        cur = db.cursor(dictionary=True)

        cur.execute(
            "SELECT id, username FROM users WHERE username=%s AND password=%s",
            (username, password)
        )

        result = cur.fetchone()
        cur.close()
        db.close()

        return result  # None if failed

    except Exception as e:
        print("[ERROR]", e)
        return None


def create_game_entry(user_id):
    try:
        db = db_connect()
        cur = db.cursor()

        cur.execute(
            "SELECT id FROM game_stats WHERE user_id=%s AND game_name=%s",
            (user_id, "Gesture Draw Game")
        )

        if not cur.fetchone():
            cur.execute("""
                INSERT INTO game_stats 
                (user_id, game_name, high_score, total_time, total_plays, avg_time)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, "Gesture Draw Game", 0, 0, 0, 0))

            db.commit()

        cur.close()
        db.close()

    except Exception as e:
        print("[ERROR saving game entry]", e)


# ---------- MAIN ----------
def main():
    username_box = InputBox(350, 260, 220, 40)
    password_box = InputBox(350, 320, 220, 40, hidden=True)

    login_btn = pygame.Rect(350, 390, 220, 45)
    register_btn = pygame.Rect(350, 450, 220, 40)

    message = ""

    def submit_login():
        nonlocal message
        username = username_box.text.strip()
        password = password_box.text.strip()

        if not username or not password:
            message = "⚠ Please fill all fields"
            return

        user_data = check_login(username, password)

        if user_data:
            user_id = user_data["id"]
            username = user_data["username"]

            # ---------- SAVE SESSION ----------
            with open("session.txt", "w") as f:
                f.write(str(user_id))  # store user_id safely

            # ---------- CREATE GAME ENTRY ----------
            create_game_entry(user_id)

            pygame.quit()
            subprocess.Popen([sys.executable, "main.py"])
            sys.exit()
        else:
            message = "❌ Invalid username or password"

    # ---------- LOOP ----------
    while True:
        screen.fill(BG)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            username_box.handle_event(event)
            password_box.handle_event(event)

            # ENTER submits login
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                submit_login()

            # Mouse click buttons
            if event.type == pygame.MOUSEBUTTONDOWN:
                if login_btn.collidepoint(event.pos):
                    submit_login()

                if register_btn.collidepoint(event.pos):
                    pygame.quit()
                    subprocess.Popen([sys.executable, "register.py"])
                    sys.exit()

        # ---------- UI ----------
        screen.blit(title_font.render("Login", True, WHITE), (380, 160))

        screen.blit(font.render("Username", True, GRAY), (350, 230))
        screen.blit(font.render("Password", True, GRAY), (350, 290))

        username_box.draw()
        password_box.draw()

        pygame.draw.rect(screen, GREEN, login_btn, border_radius=6)
        pygame.draw.rect(screen, BLUE, register_btn, border_radius=6)

        screen.blit(font.render("Login", True, BG), (430, 400))
        screen.blit(font.render("Register", True, BG), (410, 458))

        if message:
            screen.blit(font.render(message, True, RED), (350, 510))

        pygame.display.update()
        clock.tick(60)


# ---------- RUN ----------
if __name__ == "__main__":
    main()
