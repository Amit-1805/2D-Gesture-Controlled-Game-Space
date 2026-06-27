import pygame
import sys
import mysql.connector
import subprocess

pygame.init()
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Register")
clock = pygame.time.Clock()

BG = (25, 35, 55)
WHITE = (240, 240, 240)
GRAY = (180, 180, 180)
RED = (220, 80, 80)
GREEN = (80, 200, 120)

font = pygame.font.SysFont("Segoe UI", 26)
title_font = pygame.font.SysFont("Segoe UI", 46, bold=True)

class InputBox:
    def __init__(self, x, y, w, h, hidden=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.active = False
        self.hidden = hidden

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(e.pos)
        if e.type == pygame.KEYDOWN and self.active:
            if e.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif e.key != pygame.K_RETURN:
                self.text += e.unicode

    def draw(self):
        pygame.draw.rect(screen, WHITE if self.active else GRAY, self.rect, 2)
        txt = "*" * len(self.text) if self.hidden else self.text
        screen.blit(font.render(txt, True, WHITE), (self.rect.x + 10, self.rect.y + 8))

def db_connect():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="game_login"
    )

def register(username, name, phone, password):
    try:
        db = db_connect()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO users(username, name, phone, password) VALUES(%s,%s,%s,%s)",
            (username, name, phone, password)
        )
        db.commit()
        db.close()
        return True
    except:
        return False

def main():
    boxes = [
        InputBox(350, 240, 220, 40),          # Username
        InputBox(350, 300, 220, 40),          # Name
        InputBox(350, 360, 220, 40),          # Phone
        InputBox(350, 420, 220, 40, hidden=True)  # Password
    ]

    submit_btn = pygame.Rect(360, 490, 200, 45)
    msg = ""

    while True:
        screen.fill(BG)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            for b in boxes:
                b.handle_event(e)

            # ENTER key submits
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                e.type = pygame.MOUSEBUTTONDOWN
                e.pos = submit_btn.center

            if e.type == pygame.MOUSEBUTTONDOWN:
                if submit_btn.collidepoint(e.pos):
                    if register(*(b.text for b in boxes)):
                        pygame.quit()
                        subprocess.Popen([sys.executable, "login.py"])
                        sys.exit()
                    else:
                        msg = "❌ Username already exists"

        labels = ["Username", "Name", "Phone Number", "Password"]
        for i, label in enumerate(labels):
            screen.blit(font.render(label, True, GRAY), (350, 210 + i * 60))
            boxes[i].draw()

        pygame.draw.rect(screen, GREEN, submit_btn, border_radius=6)
        screen.blit(font.render("Register", True, BG), (420, 500))

        if msg:
            screen.blit(font.render(msg, True, RED), (350, 560))

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
