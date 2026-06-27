import pygame
import sys
import mysql.connector
import os
import subprocess

# ---------------- SESSION CHECK ----------------
if not os.path.exists("admin_session.txt"):
    print("Access Denied")
    sys.exit()

# ---------------- DATABASE ----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="game_login"
)
cursor = db.cursor(buffered=True)

# ---------------- PYGAME INIT ----------------
pygame.init()
WIDTH, HEIGHT = 1100, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Admin Dashboard")

font = pygame.font.SysFont("arial", 20)
header_font = pygame.font.SysFont("arial", 24, bold=True)
title_font = pygame.font.SysFont("arial", 42, bold=True)

clock = pygame.time.Clock()
section = "dashboard"
message = ""

selected_user_index = 0

# ---------------- USER BUTTONS (GLOBAL) ----------------
add_btn = pygame.Rect(150, 150, 120, 40)
edit_btn = pygame.Rect(290, 150, 120, 40)
delete_btn = pygame.Rect(430, 150, 120, 40)

# ---------------- DB FUNCTIONS ----------------
def get_users():
    cursor.execute("SELECT id, username, phone FROM users")
    return cursor.fetchall()

def add_user():
    cursor.execute(
        "INSERT INTO users (username, phone) VALUES (%s, %s)",
        ("new_user", "0000000000")
    )
    db.commit()

def update_user(user_id):
    cursor.execute(
        "UPDATE users SET username=%s, phone=%s WHERE id=%s",
        ("updated_user", "9999999999", user_id)
    )
    db.commit()

def delete_user(user_id):
    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    db.commit()

# ---------------- ANALYTICS ----------------
def run_analytics():
    global message
    try:
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", "analytical_dashboard.py"])
        message = "Analytics Opened in Browser"
    except:
        message = "Error launching analytics"

# ---------------- TABLE ----------------
def draw_table(headers, data, start_x, start_y, col_widths, row_height=35):
    global selected_user_index

    x = start_x
    for i, header in enumerate(headers):
        rect = pygame.Rect(x, start_y, col_widths[i], row_height)
        pygame.draw.rect(screen, (0, 120, 200), rect)
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)

        text = header_font.render(header, True, (255, 255, 255))
        screen.blit(text, (x + col_widths[i] // 2 - text.get_width() // 2,
                           start_y + row_height // 2 - text.get_height() // 2))
        x += col_widths[i]

    y = start_y + row_height
    for index, row in enumerate(data):
        x = start_x

        rect_row = pygame.Rect(start_x, y, sum(col_widths), row_height)

        if index == selected_user_index:
            pygame.draw.rect(screen, (80, 80, 150), rect_row)
        else:
            pygame.draw.rect(screen, (35, 35, 50), rect_row)

        for i, cell in enumerate(row):
            rect = pygame.Rect(x, y, col_widths[i], row_height)
            pygame.draw.rect(screen, (80, 80, 80), rect, 1)

            text = font.render(str(cell), True, (255, 255, 255))
            screen.blit(text, (x + col_widths[i] // 2 - text.get_width() // 2,
                               y + row_height // 2 - text.get_height() // 2))
            x += col_widths[i]

        y += row_height

# ---------------- USERS ----------------
def draw_users():
    users = get_users()

    headers = ["ID", "Username", "Phone"]
    col_widths = [150, 350, 300]

    draw_table(headers, users, 150, 200, col_widths)

    return users

# ---------------- DASHBOARD ----------------
def draw_dashboard():
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    data = [["Total Users", total_users]]
    draw_table(["Metric", "Value"], data, 350, 220, [300, 200])

# ---------------- MAIN LOOP ----------------
while True:
    clock.tick(60)
    screen.fill((15, 15, 25))

    # TITLE
    title = title_font.render("ADMIN DASHBOARD", True, (0, 200, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

    # NAV BUTTONS
    dash_btn = pygame.Rect(100, 110, 150, 45)
    users_btn = pygame.Rect(270, 110, 150, 45)
    analytics_btn = pygame.Rect(440, 110, 180, 45)
    logout_btn = pygame.Rect(650, 110, 150, 45)

    pygame.draw.rect(screen, (0, 120, 200), dash_btn, border_radius=8)
    pygame.draw.rect(screen, (0, 120, 200), users_btn, border_radius=8)
    pygame.draw.rect(screen, (0, 150, 100), analytics_btn, border_radius=8)
    pygame.draw.rect(screen, (200, 50, 50), logout_btn, border_radius=8)

    screen.blit(font.render("Dashboard", True, (255, 255, 255)), (115, 122))
    screen.blit(font.render("Users", True, (255, 255, 255)), (300, 122))
    screen.blit(font.render("Analytics", True, (255, 255, 255)), (470, 122))
    screen.blit(font.render("Logout", True, (255, 255, 255)), (685, 122))

    # USERS BUTTONS DRAW
    if section == "users":
        pygame.draw.rect(screen, (0, 150, 0), add_btn)
        pygame.draw.rect(screen, (0, 120, 200), edit_btn)
        pygame.draw.rect(screen, (200, 50, 50), delete_btn)

        screen.blit(font.render("Add", True, (255, 255, 255)), (185, 160))
        screen.blit(font.render("Edit", True, (255, 255, 255)), (325, 160))
        screen.blit(font.render("Delete", True, (255, 255, 255)), (455, 160))

    # CONTENT
    if section == "dashboard":
        draw_dashboard()
    elif section == "users":
        users = draw_users()

    # MESSAGE
    if message:
        msg = font.render(message, True, (0, 255, 150))
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT - 40))

    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:

            if dash_btn.collidepoint(event.pos):
                section = "dashboard"

            elif users_btn.collidepoint(event.pos):
                section = "users"

            elif analytics_btn.collidepoint(event.pos):
                run_analytics()

            elif logout_btn.collidepoint(event.pos):
                os.remove("admin_session.txt")
                pygame.quit()
                subprocess.Popen([sys.executable, "admin_login.py"])
                sys.exit()

            if section == "users":
                users = get_users()

                # SELECT ROW
                y_start = 235
                row_height = 35
                for i in range(len(users)):
                    if pygame.Rect(150, y_start + i * row_height, 800, row_height).collidepoint(event.pos):
                        selected_user_index = i

                # BUTTON ACTIONS
                if add_btn.collidepoint(event.pos):
                    add_user()
                    message = "User Added"

                elif edit_btn.collidepoint(event.pos) and users:
                    update_user(users[selected_user_index][0])
                    message = "User Updated"

                elif delete_btn.collidepoint(event.pos) and users:
                    delete_user(users[selected_user_index][0])
                    selected_user_index = 0
                    message = "User Deleted"

    pygame.display.flip()