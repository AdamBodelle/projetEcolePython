import pygame, random, os.path
from pygame.locals import *
from fractions import Fraction
import math

main_dir = os.path.split(os.path.abspath(__file__))[0]

WIDTH, HEIGHT = 1000, 500
SCREEN_RECT = Rect(0,0,WIDTH, HEIGHT)
SCREEN = pygame.display.set_mode(SCREEN_RECT.size)

def load_image(file):
    "loads an image, prepares it for play"
    file = os.path.join(main_dir, 'resource/Image', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
    return surface.convert_alpha()

def load_images(*files):
    imgs = []
    for file in files:
        imgs.append(load_image(file))
    return imgs


class dummysound:
    def play(self): pass

def load_sound(file):
    if not pygame.mixer: return dummysound()
    file = os.path.join(main_dir, 'resource/Audio', file)
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print ('Warning, unable to load, %s' % file)
    return dummysound()


class Player(pygame.sprite.Sprite):
    speed = [10,25]
    images = []
    side = 1

    def __init__(self, screen_rect):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=screen_rect.midbottom)
        self.reloading = 0
        self.origtop = self.rect.top
        self.facing = -1
        self.hp = 5
        self.i_frame = 20

    def move(self, direction):
        if direction: self.facing = direction
        self.rect.move_ip(direction*self.speed[0], 0)
        if self.side == -1 and self.rect.top != 0:
            self.rect.move_ip(0, self.side  * self.speed[1])
        elif self.side == 1 and self.rect.top != HEIGHT-75:
            self.rect.move_ip(0, self.side  * self.speed[1])
        self.rect = self.rect.clamp(SCREEN_RECT)
        if direction > 0:
            if self.side == -1:
                self.image = self.images[2]
            else:
                self.image = self.images[0]
        elif direction < 0:
            if self.side == -1:
                self.image = self.images[3]
            else:
                self.image = self.images[1]


    def hit(self):
        if self.i_frame == 0:
            self.hp -= 1
            self.i_frame = 20

class Homer(pygame.sprite.Sprite):
    speed = [4,4]
    images = []
    spawn_rate = 10

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        random_top = random.randint(0, WIDTH)
        random_left = random.randint(0, HEIGHT)
        self.rect.top = random_top
        self.rect.left = random_left
        self.hp = 5
        self.collision_cooldown = 100

    def update(self, player):
        if player.rect.top > self.rect.top:
            self.rect.move_ip(0, self.speed[0])
        elif player.rect.top < self.rect.top:
            self.rect.move_ip(0, -self.speed[0])


        if player.rect.left > self.rect.left:
            self.rect.move_ip(self.speed[0], 0)
            self.image = self.images[1]
        elif player.rect.left < self.rect.left:
            self.rect.move_ip(-self.speed[0], 0)
            self.image = self.images[0]

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.kill()

    def attack(self, player_rect):
        if self.collision_cooldown > 0:
            self.collision_cooldown -= 1


class Bart(pygame.sprite.Sprite):
    speed = [1,1]
    images = []
    spawn_rate = 10

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        random_top = random.randint(0, WIDTH)
        random_left = random.randint(0, HEIGHT)
        self.rect.top = random_top
        self.rect.left = random_left
        self.hp = 2
        self.reloading = 100
        self.collision_cooldown = 100

    def update(self, player):
        if player.rect.top > self.rect.top:
            self.rect.move_ip(0, self.speed[0])
        elif player.rect.top < self.rect.top:
            self.rect.move_ip(0, -self.speed[0])


        if player.rect.left > self.rect.left:
            self.rect.move_ip(self.speed[0], 0)
            self.image = self.images[1]
        elif player.rect.left < self.rect.left:
            self.rect.move_ip(-self.speed[0], 0)
            self.image = self.images[0]

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.kill()

    def attack(self, player_rect):
        if self.collision_cooldown > 0:
            self.collision_cooldown -= 1

        if self.reloading > 0:
            self.reloading -= 1

        if self.reloading <= 0:
            EnemyBullet(list(self.rect.center), list(player_rect), 20, 0)
            self.reloading = 75


class Lisa(pygame.sprite.Sprite):
    speed = [2,2]
    images = []
    spawn_rate = 30

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        random_top = random.randint(0, WIDTH)
        random_left = random.randint(0, HEIGHT)
        if random.randint(0, WIDTH) < self.rect.left:
            self.x_direction = -1
        else:
            self.x_direction = 1
        if random.randint(0, HEIGHT) < self.rect.top:
            self.y_direction = -1
        else:
            self.y_direction = 1
        self.next_move = 30
        self.rect.top = random_top
        self.rect.left = random_left
        self.hp = 2
        self.reloading = 100
        self.collision_cooldown = 100

    def update(self, player):
        if self.next_move > 0:
            self.rect.move_ip(0, self.speed[0] * self.y_direction)
            self.rect.move_ip(self.speed[0] * self.x_direction, 0)

            if self.x_direction == -1:
                self.image = self.images[1]
            else:
                self.image = self.images[0]
            self.next_move -= 1
        else:
            if random.randint(0, WIDTH) < self.rect.left:
                self.x_direction = -1
            else:
                self.x_direction = 1
            if random.randint(0, HEIGHT) < self.rect.top:
                self.y_direction = -1
            else:
                self.y_direction = 1
            self.next_move = 30



    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.kill()

    def attack(self, player_rect):
        if self.collision_cooldown > 0:
            self.collision_cooldown -= 1

        if self.reloading > 0:
            self.reloading -= 1

        if self.reloading <= 0:
            random_bullet1x = list(player_rect)[0] + random.randint(-200, 200)
            random_bullet1y = list(player_rect)[1] + random.randint(-200, 200)
            random_bullet2x = list(player_rect)[0] + random.randint(-200, 200)
            random_bullet2y = list(player_rect)[1] + random.randint(-200, 200)
            EnemyBullet(list(self.rect.center), list(player_rect), 5, 1)
            EnemyBullet(list(self.rect.center), [random_bullet1x, random_bullet1y], 5, 1)
            EnemyBullet(list(self.rect.center), [random_bullet2x, random_bullet2y], 5, 1)
            self.reloading = 150


class Marge(pygame.sprite.Sprite):
    speed = [10,0]
    images = []
    spawn_rate = 1

    def __init__(self, player, direction):
        pygame.sprite.Sprite.__init__(self, self.containers)
        if direction == 1:
            self.image = self.images[0]
        else:
            self.image = self.images[1]
        self.rect = self.image.get_rect()
        if player.side == 1:
            self.rect.bottom = HEIGHT
        else:
            self.rect.top = 0
        if direction == 1:
            self.rect.left = -50
        else:
            self.rect.right = WIDTH + 50
        self.hp = 100
        self.collision_cooldown = 10
        if direction == 1:
            self.direction = 1
        else:
            self.direction = -1

    def update(self, player):
        self.rect.move_ip(self.speed[0] * self.direction, 0)
        if self.rect.left <= -100 or self.rect.left >= WIDTH + 100:
            self.kill()

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.kill()

    def attack(self, player_rect):
        if self.collision_cooldown > 0:
            self.collision_cooldown -= 1


class Bullet(pygame.sprite.Sprite):
    speed = 10
    images = []
    def __init__(self, initial_pos, target_pos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        a, b = self.rect.size
        initial_pos[0] += a / 2
        initial_pos[1] += b / 2
        self.x = initial_pos[0]
        self.y = initial_pos[1]
        distance_x = target_pos[0] - initial_pos[0]
        distance_y = target_pos[1] - initial_pos[1]

        angle = math.atan2(distance_y, distance_x)

        self.x_speed = self.speed * math.cos(angle)
        self.y_speed = self.speed * math.sin(angle)



    def update(self, player):
        if self.rect.top <= -25:
            self.kill()
        elif self.rect.left <= -25:
            self.kill()
        elif self.rect.bottom >= HEIGHT + 25:
            self.kill()
        elif self.rect.right >= WIDTH + 25:
            self.kill()

        self.rect.top = self.y
        self.rect.left = self.x
        self.x += self.x_speed
        self.y += self.y_speed


class EnemyBullet(pygame.sprite.Sprite):
    images = []
    def __init__(self, initial_pos, target_pos, speed, img):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[img]
        self.rect = self.image.get_rect()
        a, b = self.rect.size
        initial_pos[0] += a / 2
        initial_pos[1] += b / 2
        self.x = initial_pos[0]
        self.y = initial_pos[1]
        distance_x = target_pos[0] - initial_pos[0]
        distance_y = target_pos[1] - initial_pos[1]

        angle = math.atan2(distance_y, distance_x)

        self.x_speed = speed * math.cos(angle)
        self.y_speed = speed * math.sin(angle)

    def update(self, player):
        if self.rect.top <= -25:
            self.kill()
        elif self.rect.left <= -25:
            self.kill()
        elif self.rect.bottom >= HEIGHT+25:
            self.kill()
        elif self.rect.right >= WIDTH+25:
            self.kill()

        self.rect.top = self.y
        self.rect.left = self.x
        self.x += self.x_speed
        self.y += self.y_speed


class Timer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font('resource/Font/Homer_Simpson_Revised.ttf', 38)
        self.font.set_italic(1)
        self.color = Color('white')
        self.timer = 60
        self.image = 0
        self.rect = 0


    def update(self, player):
        self.image = self.font.render(str(self.timer), 0, self.color)
        self.rect = self.image.get_rect().move(WIDTH/2-50, 20)


def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

def main():
    running = True

    pygame.init()
    pygame.display.set_caption("Touhou mais c'est avec un cochon")

    # Load images, assign to sprite classes
    # (do this before the classes are used, after screen setup)
    img = load_image('cochon.png')
    Player.images = [img, pygame.transform.flip(img, 1, 0), pygame.transform.flip(img, 0, 1), pygame.transform.flip(img, 1, 1)]
    img = load_image('homer.png')
    Homer.images = [img, pygame.transform.flip(img, 1, 0)]
    img = load_image('Bart.png')
    Bart.images = [img, pygame.transform.flip(img, 1, 0)]
    img = load_image('Lisa.png')
    Lisa.images = [img, pygame.transform.flip(img, 1, 0)]
    img = load_image('marge.png')
    Marge.images = [img, pygame.transform.flip(img, 1, 0)]
    img = load_image('cob.png')
    Bullet.images = [img]
    EnemyBullet.images = load_images('Stone.png', 'bullet.png')

    current_music = load_sound('Flower of Soul ~ Another Dream (Touhou 9, PoFV) [HD].mp3')


    # Initialize Game Groups
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies_bullets = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()

    # assign default groups to each sprite class
    Homer.containers = enemies, all
    Bart.containers = enemies, all
    Lisa.containers = enemies, all
    Marge.containers = enemies, all
    Bullet.containers = bullets, all
    EnemyBullet.containers = enemies_bullets, all
    Player.containers = all
    Timer.containers = all


    # Définir les couleurs
    YELLOW = (255, 255, 0)
    HIGHLIGHT = (150, 150, 255)

    # Police pour le texte
    font = pygame.font.Font('resource/Font/Homer_Simpson_Revised.ttf', 80)

    # Boutons avec leurs positions
    menu_items = ["Jouer", "Quitter"]
    buttons = []

    # create the background, tile the bgd image
    background = load_image('Maison.jpg')
    background = pygame.transform.scale(background, SCREEN_RECT.size)
    SCREEN.blit(background, (0, 0))
    pygame.display.flip()

    for i, item in enumerate(menu_items):
        # Positionner les boutons à 50 pixels du bord gauche
        rect = pygame.Rect(225, HEIGHT // 2 - 100 + i * 150, 250, 80)
        buttons.append((item, rect))

    timer = pygame.USEREVENT + 1
    pygame.time.set_timer(timer, 1000)

    player = Player(SCREEN_RECT)
    game_timer = Timer()

    active_enemies = 0

    current_page = 'menu'



    while running:

        pygame.time.Clock().tick(60)

        mouse_pos = pygame.mouse.get_pos()
        if current_page == 'menu':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for item, rect in buttons:
                        if rect.collidepoint(mouse_pos):
                            if item == "Jouer":
                                background = load_image('salon.png')
                                background = pygame.transform.scale(background, SCREEN_RECT.size)
                                SCREEN.blit(background, (0, 0))
                                player.hp = 5
                                game_timer.timer = 60
                                current_music.play()
                                current_page = 'game'
                            elif item == "Quitter":
                                running = False

            SCREEN.blit(background, (0, 0))

            for item, rect in buttons:
                if rect.collidepoint(mouse_pos):
                    pygame.draw.rect(SCREEN, HIGHLIGHT, rect)  # Surbrillance

                # Dessiner le texte du bouton
                draw_text(item, font, YELLOW, SCREEN, rect.centerx, rect.centery)

            if current_page == 'game':
                SCREEN.blit(background, (0, 0))

            pygame.display.flip()

        elif current_page == 'game':

            if active_enemies < 5:
                if random.randint(0,100) <= 2:
                    spawn_rate_total = Homer.spawn_rate + Bart.spawn_rate + Lisa.spawn_rate
                    random_enemy = random.randint(0,100)
                    homer_spawn_chance = Homer.spawn_rate * 100 / spawn_rate_total
                    bart_spawn_chance = Bart.spawn_rate * 100 / spawn_rate_total
                    lisa_spawn_chance = Lisa.spawn_rate * 100 / spawn_rate_total
                    if random_enemy <= homer_spawn_chance:
                        Homer()
                        active_enemies += 1
                    elif random_enemy <= bart_spawn_chance + homer_spawn_chance:
                        Bart()
                        active_enemies += 1
                    elif random_enemy <= bart_spawn_chance + homer_spawn_chance + lisa_spawn_chance:
                        Lisa()
                        active_enemies += 1

            if random.randint(0, 1000) <= Marge.spawn_rate:
                Marge(player, random.randint(0,1))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if player.reloading <= 0:
                        Bullet(list(player.rect.topleft), list(pygame.mouse.get_pos()))
                        player.reloading = 5
                if event.type == timer:
                    if game_timer.timer > 0:
                        game_timer.timer -= 1

            if player.reloading > 0:
                player.reloading -= 1

            for enemy in enemies:
                enemy.attack(player.rect)

            # clear/erase the last drawn sprites
            all.clear(SCREEN, background)

            # update all the sprites
            all.update(player=player)


            keystate = pygame.key.get_pressed()

            direction = keystate[K_d] - keystate[K_q]
            if keystate[K_z] and (player.rect.top == 0 or player.rect.top == HEIGHT-75):
                player.side = -player.side
            player.move(direction)

            for enemy in pygame.sprite.spritecollide(player, enemies, 0):
                if enemy.collision_cooldown == 0:
                    player.hit()
                    enemy.collision_cooldown = 20

            for bullet in pygame.sprite.spritecollide(player, enemies_bullets, 1):
                player.hit()

            for enemy in pygame.sprite.groupcollide(enemies, bullets, 0, 1).keys():
                if enemy.hp == 1:
                    active_enemies -= 1
                enemy.hit()

            if player.i_frame > 0:
                player.i_frame -= 1


            if player.hp <= 0:
                for enemy in enemies:
                    enemy.kill()
                for bullet in bullets:
                    bullet.kill()
                for bullet in enemies_bullets:
                    bullet.kill()
                active_enemies = 0

                background = load_image('Maison.jpg')
                background = pygame.transform.scale(background, SCREEN_RECT.size)
                SCREEN.blit(background, (0, 0))
                current_music.stop()
                current_page = 'menu'


            all.draw(SCREEN)
            pygame.display.update()


    pygame.quit()

if __name__ == '__main__': main()
