import pygame
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 864
screen_height = 936

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Kurenai no Buta')

# Fonts
font = pygame.font.SysFont('Bauhaus 93', 60)
small_font = pygame.font.SysFont('Arial', 30)

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
pink = (255, 192, 203)

# Game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
game_started = False
pipe_gap = 150
pipe_frequency = 1500  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
collision_occurred = False
collision_time = 0

# Load images
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
startscreen = pygame.image.load("img/startscreen.png")
endgamescreen = pygame.image.load("img/endgame.png")
collision_img = pygame.image.load("img/colision.png")

# Load sounds
pygame.mixer.init()
sound_start = pygame.mixer.Sound('sound/startscreen.wav')
sound_fly = pygame.mixer.Sound('sound/flying_sound.ogg')
sound_collision = pygame.mixer.Sound('sound/colision.ogg')
sound_gameover = pygame.mixer.Sound('sound/game_over.wav')


# Draw text functions
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_text_center(text, font, text_col, y):
    img = font.render(text, True, text_col)
    x = (screen_width - img.get_width()) // 2
    screen.blit(img, (x, y))


# Reset game
def reset_game(flappy, pipe_group):
    global collision_occurred, collision_time, score
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    flappy.vel = 0
    flappy.index = 0
    flappy.counter = 0
    flappy.space_pressed = False
    collision_occurred = False
    collision_time = 0
    score = 0
    return score


# Show screens
def show_start_screen():
    screen.blit(startscreen, (0, 0))
    pygame.display.update()


def show_game_over_screen():
    screen.blit(endgamescreen, (0, 0))
    draw_text(str(score), font, pink, 510, 585)
    pygame.display.update()


# Classes
class Pig(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = [pygame.image.load(
            f"img/pig{n}.png") for n in range(1, 3)]
        self.index = 0
        self.counter = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = 0
        self.space_pressed = False
        self.collision_image = collision_img

    def update(self):
        global collision_occurred

        if flying:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if not game_over and game_started and not collision_occurred:
            keys = pygame.key.get_pressed()

            if keys[K_SPACE] and not self.space_pressed:
                self.space_pressed = True
                self.vel = -10
                sound_fly.stop()  # Stop any previous instance
                sound_fly.play()

            if not keys[K_SPACE]:
                self.space_pressed = False

            flap_cooldown = 5
            self.counter += 1
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index = (self.index + 1) % len(self.images)
                self.image = self.images[self.index]

            self.image = pygame.transform.rotate(
                self.images[self.index], self.vel * -2)

        elif collision_occurred and not game_over:
            self.image = self.collision_image
            sound_fly.stop()
        else:
            if game_over:
                self.image = pygame.transform.rotate(
                    self.images[self.index], -90)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        super().__init__()
        self.image = pygame.image.load("img/pipe2.png")
        self.rect = self.image.get_rect()

        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = (x, y - pipe_gap // 2)
        else:
            self.rect.topleft = (x, y + pipe_gap // 2)

    def update(self):
        if not collision_occurred:
            self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


# Main Game Function
def main():
    global ground_scroll, flying, game_over, game_started
    global last_pipe, pass_pipe, collision_occurred, collision_time, score

    # Reset states
    ground_scroll = 0
    flying = False
    game_over = False
    game_started = False
    last_pipe = pygame.time.get_ticks() - pipe_frequency
    pass_pipe = False
    collision_occurred = False
    collision_time = 0

    pipe_group = pygame.sprite.Group()
    pig_group = pygame.sprite.Group()
    flappy = Pig(100, screen_height // 2)
    pig_group.add(flappy)

    score = reset_game(flappy, pipe_group)

    start_sound_played = False
    collision_sound_played = False
    gameover_sound_played = False

    run = True
    while run:
        clock.tick(fps)

        if not game_started and not game_over:
            if not start_sound_played:
                sound_start.play()
                start_sound_played = True

            show_start_screen()

            for event in pygame.event.get():
                if event.type == QUIT:
                    run = False
                if event.type == KEYDOWN and event.key == K_SPACE:
                    game_started = True
                    flying = True
                    sound_start.stop()

        elif game_over:
            if not gameover_sound_played:
                sound_gameover.play()
                gameover_sound_played = True

            show_game_over_screen()

            for event in pygame.event.get():
                if event.type == QUIT:
                    run = False
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        main()
                        return
                    if event.key == K_ESCAPE:
                        run = False

        else:
            # Main game loop
            screen.blit(bg, (0, 0))

            pipe_group.draw(screen)
            pig_group.draw(screen)
            pig_group.update()

            screen.blit(ground_img, (ground_scroll, 768))

            if len(pipe_group) > 0 and not collision_occurred:
                pig = pig_group.sprites()[0]
                pipe = pipe_group.sprites()[0]
                if pig.rect.left > pipe.rect.left and pig.rect.right < pipe.rect.right and not pass_pipe:
                    pass_pipe = True
                if pass_pipe and pig.rect.left > pipe.rect.right:
                    score += 1
                    pass_pipe = False

            draw_text(str(score), font, white, screen_width // 2, 20)

            if not collision_occurred and (
                pygame.sprite.groupcollide(pig_group, pipe_group, False, False)
                or flappy.rect.top < 0
                or flappy.rect.bottom >= 768
            ):
                collision_occurred = True
                collision_time = pygame.time.get_ticks()
                flying = False
                if not collision_sound_played:
                    sound_collision.play()
                    collision_sound_played = True

            if collision_occurred and not game_over:
                if pygame.time.get_ticks() - collision_time >= 1000:
                    game_over = True

            if flying and not game_over and not collision_occurred:
                time_now = pygame.time.get_ticks()
                if time_now - last_pipe > pipe_frequency:
                    pipe_height = random.randint(-100, 100)
                    btm_pipe = Pipe(
                        screen_width, screen_height // 2 + pipe_height, -1)
                    top_pipe = Pipe(
                        screen_width, screen_height // 2 + pipe_height, 1)
                    pipe_group.add(btm_pipe, top_pipe)
                    last_pipe = time_now

                pipe_group.update()
                ground_scroll -= scroll_speed
                if abs(ground_scroll) > 35:
                    ground_scroll = 0
            elif not game_over:
                pipe_group.update()

            for event in pygame.event.get():
                if event.type == QUIT:
                    run = False

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
