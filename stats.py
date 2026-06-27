import pygame
import sys
import mysql.connector
import os

# ---------- INIT ----------
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("📊 My Game Stats")
clock = pygame.time.Clock()

# ---------- COLORS ----------
BG_COLOR = (30, 40, 80)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 100)
GRAY = (180, 180, 180)
DARK = (20, 20, 20)

# ---------- FONTS ----------
title_font = pygame.font.SysFont("Segoe UI", 46, bold=True)
heading_font = pygame.font.SysFont("Segoe UI", 30, bold=True)
text_font = pygame.font.SysFont("Segoe UI", 24)

# ---------- SESSION ----------
SESSION_FILE = "session.txt"

# ---------- DATABASE ----------
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = ""
DB_NAME = "game_login"


# ---------- GET USER ID ----------
def get_user_id():
    if not os.path.exists(SESSION_FILE):
        return None
    with open(SESSION_FILE, "r") as f:
        return f.read().strip()


# ---------- DATABASE CONNECTION ----------
def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )


# ---------- GET USERNAME ----------
def get_username(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()

        return result[0] if result else "Guest"

    except Exception as e:
        print("DB Error:", e)
        return "Guest"

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


# ---------- GET USER GAME STATS ----------
def get_user_game_stats(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT game_name, high_score, total_plays, total_time
            FROM game_stats
            WHERE user_id = %s
        """, (user_id,))

        return cursor.fetchall()

    except Exception as e:
        print("DB Error:", e)
        return []

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


# ---------- DRAW CARD ----------
def draw_card(x, y, width, height):
    pygame.draw.rect(screen, DARK, (x, y, width, height), border_radius=10)
    pygame.draw.rect(screen, WHITE, (x, y, width, height), 2, border_radius=10)


# ---------- MAIN SCREEN ----------
def main():
    user_id = get_user_id()

    if not user_id:
        print("❌ No session found")
        pygame.quit()
        sys.exit()

    username = get_username(user_id)
    stats = get_user_game_stats(user_id)

    while True:
        screen.fill(BG_COLOR)

        # ---------- EVENTS ----------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # ---------- TITLE ----------
        title = title_font.render("📊 My Game Stats", True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 50)))

        # ---------- USER ----------
        user_text = heading_font.render(f"👤 Player: {username}", True, YELLOW)
        screen.blit(user_text, (50, 120))

        # ---------- STATS ----------
        y = 180

        if not stats:
            no_data = text_font.render("No stats available yet!", True, GRAY)
            screen.blit(no_data, (50, y))
        else:
            for game, score, plays, time in stats:
                draw_card(50, y, 800, 100)

                screen.blit(text_font.render(f"🎮 Game: {game}", True, WHITE), (70, y + 10))
                screen.blit(text_font.render(f"🏆 High Score: {score}", True, WHITE), (70, y + 35))
                screen.blit(text_font.render(f"🔁 Plays: {plays}", True, WHITE), (300, y + 35))
                screen.blit(text_font.render(f"⏱ Time: {round(time,2)} sec", True, WHITE), (500, y + 35))

                y += 120

        pygame.display.update()
        clock.tick(60)


# ---------- RUN ----------
if __name__ == "__main__":
    main()