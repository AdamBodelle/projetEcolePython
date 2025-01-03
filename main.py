import pygame, random, os.path
from pygame.locals import *
import math
import numpy as np

main_dir = os.path.split(os.path.abspath(__file__))[0]

WIDTH, HEIGHT = 1200, 600 # Dimension de la fenêtre
SCREEN_RECT = Rect(0,0,WIDTH, HEIGHT)
SCREEN = pygame.display.set_mode(SCREEN_RECT.size)
SCORE_FILE = "resource/score_save/score.txt"  # Fichier pour sauvegarder les scores

# Fonction pour charger une image dans les ressources
def load_image(file):
    file = os.path.join(main_dir, 'resource/Image', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
    return surface.convert_alpha()

# Fonction pour charger plusieurs images
def load_images(*files):
    imgs = []
    for file in files:
        imgs.append(load_image(file))
    return imgs


class dummysound:
    def play(self): pass

# Fonction pour charger un fichier audio
def load_sound(file):
    if not pygame.mixer: return dummysound()
    file = os.path.join(main_dir, 'resource/Audio', file)
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print ('Warning, unable to load, %s' % file)
    return dummysound()


# Vérifie si SCORE_FILE existe et contient une valeur valide
if not os.path.exists(SCORE_FILE) or not open(SCORE_FILE).readlines():
    with open(SCORE_FILE, "w") as file:
        file.write("1\n")  # Initialise le score à 1

# Fonction pour récupérer le score dans le fichier SCORE_FILE
def load_score():
    with open(SCORE_FILE, "r") as file:
        file_content = file.readlines()
        content = []
        for line in file_content:
            content.append(int(line.rstrip('\n')))
        if content[0]:
            return content
        else:
            print(f"Invalid score file content: '{content}'. Resetting score to 0.")
            return 0

# Fonction pour sauvegarder un score
def save_score(score):
    with open(SCORE_FILE, "a") as file:
        file.write(str(score)+'\n')


# Classe pour le joueur
class Player(pygame.sprite.Sprite):
    speed = [10,25]
    images = []
    side = 1
    base_hp = 10
    victory = 0

    def __init__(self, screen_rect):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=screen_rect.midbottom)
        self.reloading = 0
        self.facing = -1
        self.hp = Player.base_hp
        self.i_frame = 0

    def move(self, direction):
        # Mouvement horizontal
        if direction: self.facing = direction
        self.rect.move_ip(direction*self.speed[0], 0)

        # Mouvement vertical
        if self.side == -1 and self.rect.top != 0:
            self.rect.move_ip(0, self.side  * self.speed[1])
        elif self.side == 1 and self.rect.top != HEIGHT-75:
            self.rect.move_ip(0, self.side  * self.speed[1])
        self.rect = self.rect.clamp(SCREEN_RECT)

        # Ajustement du sprite selon le côté et la direction du joueur
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

    # Fonction appelée lorsque le joueur est touché
    def hit(self):
        self.hp -= 1
        self.i_frame = 20  # Ajoute des frame d'invincibilité lorsque le joueur est touché
        Life.amount -= 1

# Classe pour l'ennemi Homer
class Homer(pygame.sprite.Sprite):
    speed = [4,4]
    images = []
    spawn_rate = 20

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        # Apparaît à un endroit aléatoire de l'écran
        random_top = random.randint(0, HEIGHT)
        random_left = random.randint(0, WIDTH)
        self.rect.top = random_top
        self.rect.left = random_left
        self.hp = 5
        self.collision_cooldown = 100

    def update(self, player):
        # Mouvement vertical selon la position du joueur
        if player.rect.top > self.rect.top:
            self.rect.move_ip(0, self.speed[0])
        elif player.rect.top < self.rect.top:
            self.rect.move_ip(0, -self.speed[0])

        # Mouvement horizontal selon la position du joueur
        if player.rect.left > self.rect.left:
            self.rect.move_ip(self.speed[0], 0)
            self.image = self.images[1]
        elif player.rect.left < self.rect.left:
            self.rect.move_ip(-self.speed[0], 0)
            self.image = self.images[0]

    # Fonction appelée lorsque l'ennemi est touché
    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            Score.value += round(3000 / Homer.spawn_rate)
            self.kill()

    # Fonction qui gère les attaques et leur temps de rechargement
    def attack(self, player_rect):
        if self.collision_cooldown > 0:
            self.collision_cooldown -= 1

# Classe pour l'ennemi Bart
class Bart(pygame.sprite.Sprite):
    speed = [1,1]
    images = []
    spawn_rate = 25

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        # Apparaît à un endroit aléatoire de l'écran
        random_top = random.randint(0, HEIGHT)
        random_left = random.randint(0, WIDTH)
        self.rect.top = random_top
        self.rect.left = random_left
        self.hp = 2
        self.reloading = 100
        self.collision_cooldown = 100

    def update(self, player):
        # Mouvement vertical selon la position du joueur
        if player.rect.top > self.rect.top:
            self.rect.move_ip(0, self.speed[0])
        elif player.rect.top < self.rect.top:
            self.rect.move_ip(0, -self.speed[0])

        # Mouvement horizontal selon la position du joueur
        if player.rect.left > self.rect.left:
            self.rect.move_ip(self.speed[0], 0)
            self.image = self.images[1]
        elif player.rect.left < self.rect.left:
            self.rect.move_ip(-self.speed[0], 0)
            self.image = self.images[0]

    # Fonction appelée lorsque l'ennemi est touché
    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            Score.value += round(3000 / Bart.spawn_rate)
            self.kill()

    # Fonction qui gère les attaques et leur temps de rechargement
    def attack(self, player_rect):
        if self.collision_cooldown > 0:
            self.collision_cooldown -= 1

        if self.reloading > 0:
            self.reloading -= 1

        if self.reloading <= 0:
            EnemyBullet(list(self.rect.center), list(player_rect), 20, 0)
            self.reloading = 75

# Classe pour l'ennemi Lisa
class Lisa(pygame.sprite.Sprite):
    speed = [2,2]
    images = []
    spawn_rate = 15

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        random_top = random.randint(0, HEIGHT)
        random_left = random.randint(0, WIDTH)
        # Choisi un point aléatoire de l'écran avant de s'y déplacer
        if random.randint(0, WIDTH) < list(self.rect.center)[0]:
            self.x_direction = -1
        else:
            self.x_direction = 1
        if random.randint(0, HEIGHT) <  list(self.rect.center)[1]:
            self.y_direction = -1
        else:
            self.y_direction = 1
        self.next_move = 30 # Délais avant de choisir un autre point
        self.rect.top = random_top
        self.rect.left = random_left
        self.hp = 3
        self.reloading = 100
        self.collision_cooldown = 100

    def update(self, player):
        if self.next_move > 0:
            # Se déplace vers le point sélectionné
            self.rect.move_ip(0, self.speed[0] * self.y_direction)
            self.rect.move_ip(self.speed[0] * self.x_direction, 0)

            if self.x_direction == -1:
                self.image = self.images[1]
            else:
                self.image = self.images[0]
            self.next_move -= 1
        else:
            # Choisi un point aléatoire de l'écran
            if random.randint(0, WIDTH) <  list(self.rect.center)[0]:
                self.x_direction = -1
            else:
                self.x_direction = 1
            if random.randint(0, HEIGHT) <  list(self.rect.center)[1]:
                self.y_direction = -1
            else:
                self.y_direction = 1
            self.next_move = 30

    # Fonction appelée lorsque l'ennemi est touché
    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            Score.value += round(3000 / Lisa.spawn_rate)
            self.kill()

    # Fonction qui gère les attaques et leur temps de rechargement
    def attack(self, player_rect):
        if self.collision_cooldown > 0:
            self.collision_cooldown -= 1

        if self.reloading > 0:
            self.reloading -= 1

        if self.reloading <= 0:
            # Tir une balle en direction du joueur et deux autres à proximité de celui-ci
            random_bullet1x = list(player_rect)[0] + random.randint(-200, 200)
            random_bullet1y = list(player_rect)[1] + random.randint(-200, 200)
            random_bullet2x = list(player_rect)[0] + random.randint(-200, 200)
            random_bullet2y = list(player_rect)[1] + random.randint(-200, 200)
            EnemyBullet(list(self.rect.center), list(player_rect), 5, 1)
            EnemyBullet(list(self.rect.center), [random_bullet1x, random_bullet1y], 5, 1)
            EnemyBullet(list(self.rect.center), [random_bullet2x, random_bullet2y], 5, 1)
            self.reloading = 150

# Classe pour l'ennemi Maggied
class Maggie(pygame.sprite.Sprite):
    speed = [6,6]
    images = []
    spawn_rate = 10

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        random_top = random.randint(0, HEIGHT)
        random_left = random.randint(0, WIDTH)
        # Choisi un point aléatoire de l'écran avant de s'y déplacer
        if random.randint(0, WIDTH) < list(self.rect.center)[0]:
            self.x_direction = -1
        else:
            self.x_direction = 1
        if random.randint(0, HEIGHT) < list(self.rect.center)[1]:
            self.y_direction = -1
        else:
            self.y_direction = 1
        self.next_move = 15 # Délais avant de choisir un autre point
        self.rect.top = random_top
        self.rect.left = random_left
        self.hp = 2
        self.collision_cooldown = 100

    def update(self, player):
        if self.next_move > 0:
            # Se déplace vers le point sélectionné
            self.rect.move_ip(0, self.speed[0] * self.y_direction)
            self.rect.move_ip(self.speed[0] * self.x_direction, 0)

            if self.x_direction == -1:
                self.image = self.images[1]
            else:
                self.image = self.images[0]
            self.next_move -= 1
        else:
            # Choisi un point aléatoire de l'écran
            if random.randint(0, WIDTH) < list(self.rect.center)[0]:
                self.x_direction = -1
            else:
                self.x_direction = 1
            if random.randint(0, HEIGHT) < list(self.rect.center)[1]:
                self.y_direction = -1
            else:
                self.y_direction = 1
            self.next_move = 15

    # Fonction appelée lorsque l'ennemi est touché
    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            Score.value +=  round(3000 / Maggie.spawn_rate)
            self.kill()

    # Fonction qui gère les attaques et leur temps de rechargement
    def attack(self, player_rect):
        if self.collision_cooldown > 0:
            self.collision_cooldown -= 1

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
        # Apparaît du même coté que le joueur et se déplace selon la direction en paramètre
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

    # Fonction appelée lorsque l'ennemi est touché
    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.kill()

    # Fonction qui gère les attaques et leur temps de rechargement
    def attack(self, player_rect):
        if self.collision_cooldown > 0:
            self.collision_cooldown -= 1


class Abraham(pygame.sprite.Sprite):
    speed = [4,4]
    images = []

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        # Choisi un point aléatoire de l'écran avant de s'y déplacer
        if random.randint(0, WIDTH) <  list(self.rect.center)[0]:
            self.x_direction = -1
        else:
            self.x_direction = 1
        if random.randint(0, HEIGHT) <  list(self.rect.center)[1]:
            self.y_direction = -1
        else:
            self.y_direction = 1
        self.next_move = 40 # Délais avant de choisir un autre point
        self.rect.top = HEIGHT/2-100
        self.rect.left = WIDTH/2-50
        self.hp = 50
        self.reloading = 40
        self.reloading2 = 75
        self.reloading3 = 15
        self.collision_cooldown = 100

    def update(self, player):
        if self.next_move > 0:
            # Se déplace vers le point sélectionné
            self.rect.move_ip(0, self.speed[0] * self.y_direction)
            self.rect.move_ip(self.speed[0] * self.x_direction, 0)

            if self.x_direction == -1:
                self.image = self.images[1]
            else:
                self.image = self.images[0]
            self.next_move -= 1
        else:
            # Choisi un point aléatoire de l'écran
            if random.randint(0, WIDTH) <  list(self.rect.center)[0]:
                self.x_direction = -1
            else:
                self.x_direction = 1
            if random.randint(0, HEIGHT) <  list(self.rect.center)[1]:
                self.y_direction = -1
            else:
                self.y_direction = 1
            self.next_move = 40

    # Fonction appelée lorsque l'ennemi est touché
    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            Score.value += 2000
            Player.victory = 1 # Si cet ennemi meurt la partie est gagnée
            self.kill()

    # Fonction qui gère les attaques et leur temps de rechargement
    def attack(self, player_rect):
        if self.collision_cooldown > 0:
            self.collision_cooldown -= 1

        if self.reloading > 0:
            self.reloading -= 1

        if self.reloading2 > 0:
            self.reloading2 -= 1

        if self.reloading3 > 0:
            self.reloading3 -= 1

        if self.reloading <= 0:
            # Tir une balle vers le joueur
            EnemyBullet(list(self.rect.center), list(player_rect), 7, 3)
            self.reloading = 40

        if self.reloading2 <= 0:
            # Tir des balles dans toutes les directions
            pos = list(self.rect.center)
            EnemyBullet(list(self.rect.center), [pos[0]+200, pos[1]], 10, 2)
            EnemyBullet(list(self.rect.center), [pos[0]-200, pos[1]], 10, 2)
            EnemyBullet(list(self.rect.center), [pos[0], pos[1]+200], 10, 2)
            EnemyBullet(list(self.rect.center), [pos[0], pos[1]-200], 10, 2)

            EnemyBullet(list(self.rect.center), [pos[0]+200, pos[1]+200], 10, 2)
            EnemyBullet(list(self.rect.center), [pos[0]+200, pos[1]-200], 10, 2)
            EnemyBullet(list(self.rect.center), [pos[0]-200, pos[1]+200], 10, 2)
            EnemyBullet(list(self.rect.center), [pos[0]-200, pos[1]-200], 10, 2)
            self.reloading2 = 75

        if self.reloading3 <= 0:
            # Tir une balle dans une direction aléatoire
            pos = list(self.rect.center)
            random_bullet1x = pos[0] + random.randint(-200, 200)
            random_bullet1y = pos[1] + random.randint(-200, 200)
            EnemyBullet(list(self.rect.center), [random_bullet1x, random_bullet1y], 10, 2)
            self.reloading3 = 15


# Classe pour les balles du joueur
class Bullet(pygame.sprite.Sprite):
    speed = 15
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

# Classe pour les balles des ennemis
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

# Classe pour le timer de la partie
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
        if self.timer != -1:
            self.image = self.font.render(str(self.timer), 0, self.color)
        else:
            self.image = self.font.render('Boss', 0, self.color)
        self.rect = self.image.get_rect().move(WIDTH/2-50, 20)


# Classe pour la barre de vie du joueur
class Life(pygame.sprite.Sprite):
    images = []
    amount = 0

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.top = 5
        self.rect.left = 5 + self.amount * 30
        self.id = self.amount
        Life.amount += 1

    def update(self, player):
        if self.id >= self.amount:
            self.kill()

# Clase pour le score de la partie
class Score(pygame.sprite.Sprite):
    value = 0

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font('resource/Font/Homer_Simpson_Revised.ttf', 38)
        self.font.set_italic(1)
        self.color = Color('white')
        self.image = 0
        self.rect = 0


    def update(self, player):
        self.image = self.font.render(str(Score.value), 0, self.color)
        self.rect = self.image.get_rect().move(WIDTH-200, 20)

# Fonction pour écrire un texte
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

# Fonction pour recharger l'affichage des scores
def reload_score(score_array):
    scores_text = []
    for i, item in enumerate(score_array):
        if i > 2:
            break
        rect = pygame.Rect(800, HEIGHT // 2 - 150 + i * 100, 250, 80)
        scores_text.append((str(item), rect))
    return scores_text


def main():
    running = True

    pygame.init()
    pygame.display.set_caption("Touhou : Spider Cochon")

    # Chargement des images
    img = load_image('cochon.png')
    Player.images = [img, pygame.transform.flip(img, 1, 0), pygame.transform.flip(img, 0, 1), pygame.transform.flip(img, 1, 1)]
    img = load_image('homer.png')
    Homer.images = [img, pygame.transform.flip(img, 1, 0)]
    img = load_image('Bart.png')
    Bart.images = [img, pygame.transform.flip(img, 1, 0)]
    img = load_image('Lisa.png')
    Lisa.images = [img, pygame.transform.flip(img, 1, 0)]
    img = load_image('Maggie.png')
    Maggie.images = [img, pygame.transform.flip(img, 1, 0)]
    img = load_image('marge.png')
    Marge.images = [img, pygame.transform.flip(img, 1, 0)]
    img = load_image('GrandP.png')
    Abraham.images = [img, pygame.transform.flip(img, 1, 0)]
    img = load_image('cob.png')
    Bullet.images = [img]
    EnemyBullet.images = load_images('Stone.png', 'note.png', 'bloodsmall.png', 'bloodfat.png')
    img = load_image('Bacon.png')
    Life.images = [img]

    # Chargement des scores
    game_music = [
        load_sound('Flower of Soul ~ Another Dream (Touhou 9, PoFV) [HD].mp3'),
        load_sound('Night-of-night.mp3'),
        load_sound('badApple.mp3'),
        load_sound('Flandre.mp3')
    ]
    current_game_music = game_music[random.randint(0, len(game_music)-1)]
    menu_music = load_sound('[Zenless Zone Zero OST] Dusk in The Wilderness.mp3')
    end_music = load_sound('Spider-Cochon.mp3')
    death_sound = load_sound('Touhou Death Sound Effect.mp3')
    hit_sound = load_sound('Undertale Sound Effect.mp3')
    victory_sound = load_sound('FF VII victory theme.mp3')


    # Initialisation des groupes
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies_bullets = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()

    # Affectation des groupes aux classes
    Homer.containers = enemies, all
    Bart.containers = enemies, all
    Lisa.containers = enemies, all
    Maggie.containers = enemies, all
    Marge.containers = enemies, all
    Abraham.containers = enemies, all
    Bullet.containers = bullets, all
    EnemyBullet.containers = enemies_bullets, all
    Player.containers = all
    Timer.containers = all
    Life.containers = all
    Score.containers = all


    # Définir les couleurs
    YELLOW = (255, 255, 0)
    HIGHLIGHT = (100, 0, 0)

    # Police pour le texte
    font = pygame.font.Font('resource/Font/Homer_Simpson_Revised.ttf', 80)

    # Boutons avec leurs positions
    menu_items = ["Jouer", "Quitter"]
    end_items = ["Rejouer", "Menu"]
    buttons_menu = []
    buttons_end = []
    score_tab = reversed(np.sort(load_score()))
    score_text = []

    # Creation du fond
    background = load_image('image_menu.png')
    background = pygame.transform.scale(background, SCREEN_RECT.size)
    SCREEN.blit(background, (0, 0))
    pygame.display.flip()

    for i, item in enumerate(menu_items):
        # Positionner les boutons à 50 pixels du bord gauche
        rect = pygame.Rect(50, HEIGHT // 2 - 200 + i * 150, 250, 80)
        buttons_menu.append((item, rect))

    for i, item in enumerate(end_items):
        # Positionner les boutons à 50 pixels du bord gauche
        rect = pygame.Rect(50, HEIGHT // 2 - 200 + i * 150, 250, 80)
        buttons_end.append((item, rect))

    for i, item in enumerate(score_tab):
        if i > 2:
            break
        # Positionner les boutons à 50 pixels du bord gauche
        rect = pygame.Rect(800, HEIGHT // 2 - 150 + i * 100, 250, 80)
        score_text.append((str(item), rect))

    timer = pygame.USEREVENT + 1
    pygame.time.set_timer(timer, 1000)

    # Instantiation du joueur, timer, et score
    player = Player(SCREEN_RECT)
    game_timer = Timer()
    Score()

    active_enemies = 0 # Nombre d'ennemis en vie

    current_page = 'menu' # Page actuelle

    menu_music.play()

    while running:

        pygame.time.Clock().tick(60)

        mouse_pos = pygame.mouse.get_pos()
        if current_page == 'menu':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for item, rect in buttons_menu:
                        if rect.collidepoint(mouse_pos):
                            if item == "Jouer":
                                background = load_image('salon.png')
                                background = pygame.transform.scale(background, SCREEN_RECT.size)
                                SCREEN.blit(background, (0, 0))
                                player.hp = Player.base_hp
                                Score.value = 0
                                game_timer.timer = 30
                                menu_music.stop()
                                current_game_music = game_music[random.randint(0, len(game_music)-1)]
                                current_game_music.play()
                                for i in range(Player.base_hp):
                                    Life()
                                current_page = 'game'
                            elif item == "Quitter":
                                running = False

            SCREEN.blit(background, (0, 0))

            draw_text('Classement', font, YELLOW, SCREEN, 950, HEIGHT // 2 - 200)
            # Affichage des scores
            for item, rect in score_text:

                # Dessiner le texte du bouton
                draw_text(item, font, YELLOW, SCREEN, rect.centerx, rect.centery)

            # Affichage des boutons
            for item, rect in buttons_menu:
                if rect.collidepoint(mouse_pos):
                    pygame.draw.rect(SCREEN, HIGHLIGHT, rect)  # Surbrillance

                # Dessiner le texte du bouton
                draw_text(item, font, YELLOW, SCREEN, rect.centerx, rect.centery)

            if current_page == 'game':
                SCREEN.blit(background, (0, 0))

            pygame.display.flip()


        if current_page == 'end':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for item, rect in buttons_end:
                        if rect.collidepoint(mouse_pos):
                            if item == "Rejouer":
                                background = load_image('salon.png')
                                background = pygame.transform.scale(background, SCREEN_RECT.size)
                                SCREEN.blit(background, (0, 0))
                                player.hp = Player.base_hp
                                Score.value = 0
                                game_timer.timer = 30
                                end_music.stop()
                                current_game_music = game_music[random.randint(0, len(game_music)-1)]
                                current_game_music.play()
                                for i in range(Player.base_hp):
                                    Life()
                                current_page = 'game'
                            elif item == "Menu":
                                score_tab = reversed(np.sort(load_score()))
                                score_text = reload_score(score_tab)
                                end_music.stop()
                                menu_music.play()
                                current_page = 'menu'

            SCREEN.blit(background, (0, 0))

            draw_text('Score', font, YELLOW, SCREEN, 950, HEIGHT // 2 - 100)
            draw_text(str(Score.value), font, YELLOW, SCREEN, 950, HEIGHT // 2)

            # Affichage des boutons
            for item, rect in buttons_end:
                if rect.collidepoint(mouse_pos):
                    pygame.draw.rect(SCREEN, HIGHLIGHT, rect)  # Surbrillance

                # Dessiner le texte du bouton
                draw_text(item, font, YELLOW, SCREEN, rect.centerx, rect.centery)

            if current_page == 'game':
                SCREEN.blit(background, (0, 0))

            pygame.display.flip()




        elif current_page == 'game':

            # Scipt pour gérer l'apparition des ennemis, max 5 à la fois
            if active_enemies < 5 and game_timer.timer > 0:
                if random.randint(0,100) <= 2:
                    spawn_rate_total = Homer.spawn_rate + Bart.spawn_rate + Lisa.spawn_rate + Maggie.spawn_rate
                    random_enemy = random.randint(0,100)
                    homer_spawn_chance = Homer.spawn_rate * 100 / spawn_rate_total
                    bart_spawn_chance = Bart.spawn_rate * 100 / spawn_rate_total
                    lisa_spawn_chance = Lisa.spawn_rate * 100 / spawn_rate_total
                    maggie_spawn_chance = Maggie.spawn_rate * 100 / spawn_rate_total
                    if random_enemy <= homer_spawn_chance:
                        Homer()
                        active_enemies += 1
                    elif random_enemy <= bart_spawn_chance + homer_spawn_chance:
                        Bart()
                        active_enemies += 1
                    elif random_enemy <= bart_spawn_chance + homer_spawn_chance + lisa_spawn_chance:
                        Lisa()
                        active_enemies += 1
                    elif random_enemy <= bart_spawn_chance + homer_spawn_chance + lisa_spawn_chance + maggie_spawn_chance:
                        Maggie()
                        active_enemies += 1

            # Script qui gère l'apparition de l'ennemi Marge
            if random.randint(0, 1000) <= Marge.spawn_rate and game_timer.timer > 0:
                Marge(player, random.randint(0,1))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Tir une balle si leur joueur ne recharge pas
                    if player.reloading <= 0:
                        Bullet(list(player.rect.topleft), list(pygame.mouse.get_pos()))
                        player.reloading = 5
                if event.type == timer:
                    if game_timer.timer > 0:
                        game_timer.timer -= 1
                    if game_timer.timer == 0:
                        # Lorsque le timer atteint 0 nettoie les sprites puis fait apparaitre le boss
                        for enemy in enemies:
                            enemy.kill()
                        for bullet in enemies_bullets:
                            bullet.kill()
                        active_enemies = 0
                        Abraham()
                        game_timer.timer -= 1

            # Décrémente le temps de rechargement du joueur
            if player.reloading > 0:
                player.reloading -= 1

            # Effectue les action d'attaque des ennemis
            for enemy in enemies:
                enemy.attack(player.rect)

            # Supprimer les sprites de l'écran
            all.clear(SCREEN, background)

            # Met à jour les sprites
            all.update(player=player)


            keystate = pygame.key.get_pressed()
            # Gère les déplacements du joueur
            direction = keystate[K_d] - keystate[K_q]
            if keystate[K_z] and (player.rect.top == 0 or player.rect.top == HEIGHT-75):
                player.side = -player.side
            player.move(direction)


            # Partie de gestion des collisions entre les sprites, en cas de collision avec le joueur on vérifie s'il est actuellement invincible
            for enemy in pygame.sprite.spritecollide(player, enemies, 0):
                if not enemy.collision_cooldown and not player.i_frame:
                    player.hit()
                    hit_sound.play()
                    enemy.collision_cooldown = 20

            for bullet in pygame.sprite.spritecollide(player, enemies_bullets, 1):
                if not player.i_frame:
                    player.hit()
                    hit_sound.play()

            for enemy in pygame.sprite.groupcollide(enemies, bullets, 0, 1).keys():
                if enemy.hp == 1:
                    active_enemies -= 1
                enemy.hit()

            # Décrémente la durée d'invincibilité du joueur
            if player.i_frame > 0:
                player.i_frame -= 1

            # Condition de fin de partie si le joueur meurt ou que le boss est tué
            if player.hp <= 0 or player.victory:
                if not Player.victory:
                    death_sound.play()
                else:
                    victory_sound.play()
                # On supprime tous les sprites
                for enemy in enemies:
                    enemy.kill()
                for bullet in bullets:
                    bullet.kill()
                for bullet in enemies_bullets:
                    bullet.kill()
                active_enemies = 0

                # Calcule du score et enregistrement
                Player.victory = 0
                Score.value += Life.amount * 200
                Life.amount = 0
                save_score(Score.value)

                background = load_image('image_menu.png')
                background = pygame.transform.scale(background, SCREEN_RECT.size)
                SCREEN.blit(background, (0, 0))
                current_game_music.stop()
                end_music.play()
                current_page = 'end'


            all.draw(SCREEN)
            pygame.display.update()


    pygame.quit()

if __name__ == '__main__': main()
