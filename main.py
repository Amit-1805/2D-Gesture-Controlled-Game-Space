import pygame
import subprocess
import sys
import os
import mysql.connector

# ---------- INIT ----------
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🎮 Gesture Game Hub")
clock = pygame.time.Clock()

# ---------- COLORS ----------
BG_TOP = (20, 20, 40)
BG_BOTTOM = (60, 120, 200)
WHITE = (245, 245, 245)
YELLOW = (255, 220, 100)
GRAY = (180, 180, 180)
DARK = (30, 30, 30)

# ---------- FONTS ----------
title_font = pygame.font.SysFont("Segoe UI", 56, bold=True)
menu_font = pygame.font.SysFont("Segoe UI", 30)
small_font = pygame.font.SysFont("Segoe UI", 22)

# ---------- FILES ----------
HIGHSCORE_FILE = "highscore.txt"
SESSION_FILE = "session.txt"

FRUIT_GAME = "fruit_game.py"
SPACE_GAME = "space_fighter.py"
LOGIN_FILE = "login.py"
STATS_FILE = "stats.py"   # ✅ NEW

# ---------- DATABASE CONFIG ----------
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = ""
DB_NAME = "game_login"

# ---------- LOGIN CHECK ----------
def is_logged_in():
    return os.path.exists(SESSION_FILE)

def redirect_to_login():
    pygame.quit()
    subprocess.Popen([sys.executable, LOGIN_FILE])
    sys.exit()

# ---------- GET USERNAME ----------
def get_username():
    if not os.path.exists(SESSION_FILE):
        return "Guest"

    with open(SESSION_FILE, "r") as f:
        user_id = f.read().strip()

    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else "Guest"

    except mysql.connector.Error as err:
        print("Database error:", err)
        return "Guest"

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

# ---------- GRADIENT ----------
def draw_gradient():
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(BG_TOP[0] * (1 - ratio) + BG_BOTTOM[0] * ratio)
        g = int(BG_TOP[1] * (1 - ratio) + BG_BOTTOM[1] * ratio)
        b = int(BG_TOP[2] * (1 - ratio) + BG_BOTTOM[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

# ---------- BUTTON ----------
def draw_button(text, rect, hover=False):
    color = YELLOW if hover else WHITE
    pygame.draw.rect(screen, DARK, rect, border_radius=14)
    pygame.draw.rect(screen, color, rect, 3, border_radius=14)
    label = menu_font.render(text, True, color)
    screen.blit(label, label.get_rect(center=rect.center))

# ---------- HIGHSCORE ----------
def load_highscore():
    if not os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "w") as f:
            f.write("0")
    with open(HIGHSCORE_FILE, "r") as f:
        return f.read().strip()

# ---------- LAUNCH GAME ----------
def launch_game(game_file):
    if not is_logged_in():
        redirect_to_login()

    if os.path.exists(game_file):
        pygame.quit()
        subprocess.run([sys.executable, game_file])
        sys.exit()
    else:
        print(f"❌ {game_file} not found")

# ---------- MAIN MENU ----------
def main_menu():
    if not is_logged_in():
        redirect_to_login()

    username = get_username()

    # ---------- BUTTONS ----------
    fruit_rect = pygame.Rect(340, 250, 240, 60)
    space_rect = pygame.Rect(340, 320, 240, 60)
    stats_rect = pygame.Rect(340, 390, 240, 60)   # ✅ NEW
    quit_rect  = pygame.Rect(340, 460, 240, 60)

    while True:
        draw_gradient()
        mouse_pos = pygame.mouse.get_pos()

        # ---------- EVENTS ----------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if fruit_rect.collidepoint(mouse_pos):
                    launch_game(FRUIT_GAME)

                elif space_rect.collidepoint(mouse_pos):
                    launch_game(SPACE_GAME)

                elif stats_rect.collidepoint(mouse_pos):   # ✅ NEW
                    pygame.quit()
                    subprocess.run([sys.executable, STATS_FILE])
                    sys.exit()

                elif quit_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        # ---------- TITLE ----------
        title_surface = title_font.render("Gesture Game Hub", True, WHITE)
        screen.blit(title_surface, title_surface.get_rect(center=(WIDTH // 2, 120)))

        # ---------- WELCOME ----------
        welcome = small_font.render(f"Welcome, {username}!", True, YELLOW)
        screen.blit(welcome, welcome.get_rect(center=(WIDTH // 2, 160)))

        subtitle = small_font.render("Play camera & gesture controlled games", True, GRAY)
        screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 190)))

        # ---------- HIGHSCORE ----------
        hs = load_highscore()
        hs_text = small_font.render(f"🏆 Best Score: {hs}", True, WHITE)
        screen.blit(hs_text, hs_text.get_rect(center=(WIDTH // 2, 220)))

        # ---------- BUTTONS ----------
        draw_button("🍎 Fruit Catcher", fruit_rect, fruit_rect.collidepoint(mouse_pos))
        draw_button("🚀 Space Fighter", space_rect, space_rect.collidepoint(mouse_pos))
        draw_button("📊 View Stats", stats_rect, stats_rect.collidepoint(mouse_pos))  # ✅ NEW
        draw_button("❌ Quit", quit_rect, quit_rect.collidepoint(mouse_pos))

        # ---------- FOOTER ----------
        footer = small_font.render("Python • Pygame • MediaPipe", True, GRAY)
        screen.blit(footer, footer.get_rect(center=(WIDTH // 2, HEIGHT - 40)))

        pygame.display.update()
        clock.tick(60)

# ---------- RUN ----------
if __name__ == "__main__":
    main_menu()