import pygame
import sys
import mysql.connector

# ---------------- DATABASE ----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="game_login"
)
cursor = db.cursor()

pygame.init()
WIDTH, HEIGHT = 600, 450
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Admin Login")

font = pygame.font.SysFont("arial", 28)
big_font = pygame.font.SysFont("arial", 40)

username = ""
password = ""
active_field = "username"
message = ""

clock = pygame.time.Clock()

def draw_ui():
    screen.fill((18, 18, 25))

    # Login Card
    card = pygame.Rect(100, 70, 400, 300)
    pygame.draw.rect(screen, (35, 35, 50), card, border_radius=15)

    # Title
    title = big_font.render("ADMIN PANEL LOGIN", True, (0, 200, 255))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 90))

    # Input Boxes
    u_box = pygame.Rect(170, 160, 260, 45)
    p_box = pygame.Rect(170, 220, 260, 45)
    login_btn = pygame.Rect(240, 290, 120, 45)

    # Highlight active field
    pygame.draw.rect(screen, (0,200,255) if active_field=="username" else (100,100,100), u_box, 2, border_radius=8)
    pygame.draw.rect(screen, (0,200,255) if active_field=="password" else (100,100,100), p_box, 2, border_radius=8)

    pygame.draw.rect(screen, (0,150,0), login_btn, border_radius=10)

    # Labels
    screen.blit(font.render("Username", True, (200,200,200)), (170,130))
    screen.blit(font.render("Password", True, (200,200,200)), (170,190))

    # Text
    screen.blit(font.render(username, True, (255,255,255)), (180,170))
    screen.blit(font.render("*"*len(password), True, (255,255,255)), (180,230))

    screen.blit(font.render("LOGIN", True, (255,255,255)), (260,300))

    if message:
        screen.blit(font.render(message, True, (255,80,80)), (WIDTH//2 - 120, 350))

    pygame.display.flip()
    return u_box, p_box, login_btn


# ---------------- MAIN LOOP ----------------
while True:
    clock.tick(60)
    u_box, p_box, login_btn = draw_ui()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if u_box.collidepoint(event.pos):
                active_field = "username"
            elif p_box.collidepoint(event.pos):
                active_field = "password"
            elif login_btn.collidepoint(event.pos):
                cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s",
                               (username, password))
                if cursor.fetchone():
                    with open("admin_session.txt", "w") as f:
                        f.write(username)
                    pygame.quit()
                    import admin_panel
                    sys.exit()
                else:
                    message = "Invalid Credentials"

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s",
                               (username, password))
                if cursor.fetchone():
                    with open("admin_session.txt", "w") as f:
                        f.write(username)
                    pygame.quit()
                    import admin_panel
                    sys.exit()
                else:
                    message = "Invalid Credentials"

            elif event.key == pygame.K_BACKSPACE:
                if active_field == "username":
                    username = username[:-1]
                else:
                    password = password[:-1]
            else:
                if active_field == "username":
                    username += event.unicode
                else:
                    password += event.unicode
