import pygame
import pickle
from os import path

pygame.init()

clock = pygame.time.Clock()
fps = 180

# game window
menu = True
level_num = 1
cur_level = 1
max_level = 2
gm_ov = 0
block_sz = 30
lever_state = 0
screen_width = 800
screen_height = 740

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Lvl 1')

# loading components
bg_img = pygame.image.load('img/bg.jpg')
bg_size = (1000, 800)
bg_img = pygame.transform.scale(bg_img, bg_size)
grass_img = pygame.image.load('img/grass.png')
grass_img = pygame.transform.scale(grass_img, (block_sz, block_sz / 2))  # Find appropriate block_sz pic here
dirt_img = pygame.image.load('img/dirt.png')
dirt_img = pygame.transform.scale(dirt_img, (block_sz, block_sz))  # Find appropriate block_sz pic here
stonewall_img = pygame.image.load('img/stonewall.png')
stonewall_img = pygame.transform.scale(stonewall_img, (block_sz, block_sz))
lava_img = pygame.image.load('img/lava.jpg')
lava_img = pygame.transform.scale(lava_img, (block_sz, block_sz / 2))
water_img = pygame.image.load('img/water.jpg')
water_img = pygame.transform.scale(water_img, (block_sz, block_sz / 2))
void_img = pygame.image.load('img/void.jpg')
void_img = pygame.transform.scale(void_img, (block_sz, block_sz / 2))
res_img = pygame.image.load('img/restart.png')
res_img = pygame.transform.scale(res_img, (block_sz * 4, block_sz * 1.5))
exit_img = pygame.image.load('img/exit.png')
exit_img = pygame.transform.scale(exit_img, (block_sz * 4, block_sz * 1.5))
start_img = pygame.image.load('img/start.png')
start_img = pygame.transform.scale(start_img, (block_sz * 4, block_sz * 1.5))
door_img = pygame.image.load('img/door.png')
door_img = pygame.transform.scale(door_img, (block_sz, 48.6))
lever_img = pygame.image.load('img/lever_right.png')
lever_img = pygame.transform.scale(lever_img, (block_sz, 48.6))


def reset_lvl(lvl):
    player1.reset(block_sz + 1, screen_height - 58)
    player2.reset(block_sz + 1, screen_height - 158)
    lava_group.empty()
    water_group.empty()
    void_group.empty()
    door_group.empty()
    platform_group.empty()
    lever_group.empty()

    t_level = open(f'lvl{lvl}.pkl', 'rb')
    cmap = pickle.load(t_level)
    newmap = CreateWorld(cmap)

    return newmap

class Buttons():
    def __init__(self, x, y, img):
        self.img = img
        self.rect = self.img.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.state = 0

    def screen(self):
        event = False
        wh = pygame.mouse.get_pos()

        if self.rect.collidepoint(wh):
            if pygame.mouse.get_pressed()[0] and self.state == 0:
                event = True
                self.state = 1
            if not pygame.mouse.get_pressed()[0]:
                self.state = 0

        screen.blit(self.img, self.rect)

        return event

# 2 Character - Player
class Playing_entity_one:
    def __init__(self, x_cord, y_cord):
        self.reset(x_cord, y_cord)


    def update(self, game_state):
        correcting = 20
        x_velocity = 1
        x_ch = 0
        y_ch = 0
        i = 0

        if game_state == 0:
            p_key = pygame.key.get_pressed()
            if p_key[pygame.K_LEFT]:
                x_ch -= x_velocity
                self.i = 1

            if p_key[pygame.K_RIGHT]:
                x_ch += x_velocity
                self.i = 0

            if p_key[pygame.K_UP] and self.y_state == 1:
                self.y_velocity = -6
                self.y_state = True

            if not p_key[pygame.K_UP]:
                self.y_state = False

            # Fall
            self.y_velocity += 0.3
            if self.y_velocity > 0.5:
                self.y_velocity = 0.5

            y_ch += self.y_velocity

        self.y_state = 0
        # Interaction / Collision
        for blocks in newmap.blocks:
            # horizontal dir
            if blocks[1].colliderect(self.rect.x + x_ch + 1, self.rect.y, self.w, self.h):
                x_ch = 0

            if blocks[1].colliderect(self.rect.x + x_ch - 1, self.rect.y, self.w, self.h):
                x_ch = 0

            # vertical dir
            if blocks[1].colliderect(self.rect.x, self.rect.y + y_ch + 1, self.w, self.h):
                if self.y_velocity < 0:
                    y_ch = blocks[1].bottom - self.rect.top
                    self.y_velocity = 0
                else:
                    y_ch = blocks[1].top - self.rect.bottom
                    self.y_velocity = 0
                    self.y_state = 1

        #game over

            # platforms
            for elements in platform_group:
                # horizontal dir
                if elements.rect.colliderect(self.rect.x + x_ch + 1, self.rect.y, self.w, self.h):
                    x_ch = 0

                if elements.rect.colliderect(self.rect.x + x_ch - 1, self.rect.y, self.w, self.h):
                    x_ch = 0

                # vertical dir
                if elements.rect.colliderect(self.rect.x, self.rect.y + y_ch + 1, self.w, self.h):
                    if abs(self.rect.top + y_ch - elements.rect.bottom) < correcting:
                        self.y_velocity = 0

                    elif abs(self.rect.bottom + y_ch - elements.rect.top) < correcting:
                        self.rect.bottom = elements.rect.top
                        self.y_state = 1
                        y_ch = 0

        # movement
        self.rect.x += x_ch
        self.rect.y += y_ch

        self.p_image = self.imgs[self.i]
        screen.blit(self.p_image, self.rect)

        return game_state

    def reset(self, x_cord, y_cord):
        self.imgs = []
        self.i = 0
        player = pygame.image.load('img/player1.png')
        player = pygame.transform.scale(player, (25, 48.6))
        player_b = pygame.transform.flip(player, True, False)
        self.imgs.append(player)
        self.imgs.append(player_b)
        self.p_image = pygame.transform.scale(player, (25, 48.6))
        self.rect = self.p_image.get_rect()
        self.w = self.p_image.get_width()
        self.h = self.p_image.get_height()
        self.rect.x = x_cord
        self.rect.y = y_cord
        self.y_state = 0
        self.y_velocity = 0
        self.y_state = False

class Playing_entity_two:
    def __init__(self, x_cord, y_cord):
        self.reset(x_cord, y_cord)

    def update(self, game_state):
        correcting = 20
        x_velocity = 1
        x_ch = 0
        y_ch = 0

        if game_state == 0:
            p_key = pygame.key.get_pressed()
            if p_key[pygame.K_a]:
                x_ch -= x_velocity
                self.i = 1

            if p_key[pygame.K_d]:
                x_ch += x_velocity
                self.i = 0

            if p_key[pygame.K_w] and self.y_state == 1:
                self.y_velocity = -6
                self.y_state = True

            if not p_key[pygame.K_w]:
                self.y_state = False

            # Fall
            self.y_velocity += 0.3
            if self.y_velocity > 0.5:
                self.y_velocity = 0.5

            y_ch += self.y_velocity

        self.y_state = 0
        # Interaction / Collision
        for blocks in newmap.blocks:
            # horizontal dir
            if blocks[1].colliderect(self.rect.x + x_ch + 1, self.rect.y, self.w, self.h):
                x_ch = 0

            if blocks[1].colliderect(self.rect.x + x_ch - 1, self.rect.y, self.w, self.h):
                x_ch = 0

            # vertical dir
            if blocks[1].colliderect(self.rect.x, self.rect.y + y_ch + 1, self.w, self.h):
                if self.y_velocity < 0:
                    y_ch = blocks[1].bottom - self.rect.top
                    self.y_velocity = 0
                else:
                    y_ch = blocks[1].top - self.rect.bottom
                    self.y_velocity = 0
                    self.y_state = 1

        #game over

        #platforms
        for elements in platform_group:
            # horizontal dir
            if elements.rect.colliderect(self.rect.x + x_ch + 1, self.rect.y, self.w, self.h):
                x_ch = 0

            if elements.rect.colliderect(self.rect.x + x_ch - 1, self.rect.y, self.w, self.h):
                x_ch = 0


            # vertical dir
            if elements.rect.colliderect(self.rect.x, self.rect.y + y_ch + 1, self.w, self.h):
                if abs(self.rect.top + y_ch - elements.rect.bottom) < correcting:
                    self.y_velocity = 0

                elif abs(self.rect.bottom + y_ch - elements.rect.top) < correcting:
                    self.rect.bottom = elements.rect.top
                    self.y_state = 1
                    y_ch = 0



        # movement
        self.rect.x += x_ch
        self.rect.y += y_ch

        self.p_image = self.imgs[self.i]
        screen.blit(self.p_image, self.rect)

        return game_state

    def reset(self, x_cord, y_cord):
        self.imgs = []
        self.i = 0
        player = pygame.image.load('img/player2.png')
        player = pygame.transform.scale(player, (25, 48.6))
        player_b = pygame.transform.flip(player, True, False)
        self.imgs.append(player)
        self.imgs.append(player_b)
        self.p_image = pygame.transform.scale(player, (25, 48.6))
        self.rect = self.p_image.get_rect()
        self.w = self.p_image.get_width()
        self.h = self.p_image.get_height()
        self.rect.x = x_cord
        self.rect.y = y_cord
        self.y_velocity = 0
        self.y_state = 0

# leveling
class CreateWorld:
    def __init__(self, data):
        self.blocks = []

        y_cord = 0
        for row in data:
            x_cord = 0
            for num in row:
                if num == 1:
                    grass_rec = grass_img.get_rect()
                    grass_rec.x = x_cord * block_sz
                    grass_rec.y = y_cord * block_sz
                    num = (grass_img, grass_rec)
                    self.blocks.append(num)

                if num == 2:
                    dirt_rec = dirt_img.get_rect()
                    dirt_rec.x = x_cord * block_sz
                    dirt_rec.y = y_cord * block_sz
                    num = (dirt_img, dirt_rec)
                    self.blocks.append(num)

                if num == 3:
                    stonewall_rec = stonewall_img.get_rect()
                    stonewall_rec.x = x_cord * block_sz
                    stonewall_rec.y = y_cord * block_sz
                    num = (stonewall_img, stonewall_rec)
                    self.blocks.append(num)

                if num == 4:
                    lava_one = Threats_lava(x_cord * block_sz, y_cord * block_sz + lava_img.get_height() - 10)
                    lava_group.add(lava_one)

                if num == 5:
                    water = Threats_water(x_cord * block_sz, y_cord * block_sz + water_img.get_height() - 10)
                    water_group.add(water)

                if num == 6:
                    void = Threats_void(x_cord * block_sz, y_cord * block_sz + void_img.get_height() - 10)
                    void_group.add(void)

                if num == 7:
                    door = Friend_door(x_cord * block_sz, y_cord * block_sz + door_img.get_height() - 67)
                    door_group.add(door)

                if num == 8:
                    platform = Platfrm(x_cord * block_sz, y_cord * block_sz + grass_img.get_height())
                    platform_group.add(platform)

                if num == 9:
                    lever_t = lever(x_cord * block_sz, y_cord * block_sz + lever_img.get_height() - 67)
                    lever_group.add(lever_t)

                x_cord += 1
            y_cord += 1

    def drawmap(self):
        for block in self.blocks:
            screen.blit(block[0], block[1])

# Threats
class Threats_lava(pygame.sprite.Sprite):
    def __init__(self, x_cord, y_cord):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/lava.jpg')
        self.image = pygame.transform.scale(self.image, (block_sz, block_sz / 1.2))
        self.rect = self.image.get_rect()
        self.rect.x = x_cord
        self.rect.y = y_cord

class Threats_water(pygame.sprite.Sprite):
    def __init__(self, x_cord, y_cord):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/water.jpg')
        self.image = pygame.transform.scale(self.image, (block_sz, block_sz / 1.2))
        self.rect = self.image.get_rect()
        self.rect.x = x_cord
        self.rect.y = y_cord

class Threats_void(pygame.sprite.Sprite):
    def __init__(self, x_cord, y_cord):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/void.jpg')
        self.image = pygame.transform.scale(self.image, (block_sz, block_sz / 1.2))
        self.rect = self.image.get_rect()
        self.rect.x = x_cord
        self.rect.y = y_cord

class Friend_door(pygame.sprite.Sprite):
    def __init__(self, x_cord, y_cord):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/door.png')
        self.image = pygame.transform.scale(self.image, (block_sz, 48.6))
        self.rect = self.image.get_rect()
        self.rect.x = x_cord
        self.rect.y = y_cord

class Platfrm(pygame.sprite.Sprite):
    def __init__(self, x_cord, y_cord):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/grass.png')
        self.image = pygame.transform.scale(self.image, (block_sz, block_sz / 2))
        self.rect = self.image.get_rect()
        self.rect.x = x_cord
        self.rect.y = y_cord
        self.m_dir = 1
        self.m_count = 0

    def update(self):
        self.rect.y -= self.m_dir
        self.m_count += 0.5

        if abs(self.m_count) > 45:
            self.m_dir *= -1
            self.m_count *= -1

        if self.m_count == 0:
            self.m_dir *= -1
            self.m_count *= -1


class lever(pygame.sprite.Sprite):
    def __init__(self, x_cord, y_cord):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/lever_right.png')
        self.image = pygame.transform.scale(self.image, (block_sz, 48.6))
        self.rect = self.image.get_rect()
        self.rect.x = x_cord
        self.rect.y = y_cord

    def update(self):
        if lever_state == 0:
            self.image = pygame.image.load('img/lever_left.png')

        else:
            self.image = pygame.image.load('img/lever_right.png')
        self.image = pygame.transform.scale(self.image, (block_sz, 48.6))



lvl1 = [
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 3, 3, 3, 5, 5, 3, 0, 0, 0, 0, 7, 3],
    [3, 0, 0, 0, 0, 0, 3, 4, 4, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3],
    [3, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 3, 3, 8, 0, 0, 0, 9, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 5, 5, 3, 0, 0, 9, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 3, 6, 6, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 8, 8, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 3],
    [3, 8, 8, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 1, 1, 1, 1, 1, 1, 1, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 6, 6, 3, 3, 3, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 3],
    [3, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 3, 3, 3, 3, 3, 5, 5, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3],
]

lvl2 = [
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 9, 0, 3, 3, 4, 4, 3, 5, 5, 3, 3, 3, 3, 3, 3, 3],
    [3, 0, 0, 0, 0, 0, 3, 4, 4, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3],
    [3, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 3, 3, 8, 0, 0, 0, 9, 0, 0, 0, 0, 8, 8, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 5, 5, 3, 0, 0, 9, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 3, 6, 6, 3, 3, 3, 3, 3, 3, 3, 3, 3, 5, 5, 8, 8, 3],
    [3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 3],
    [3, 3, 8, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 1, 1, 1, 1, 1, 1, 1, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 4, 4, 3, 3, 3, 6, 6, 3, 3, 3, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 3],
    [3, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 3, 3, 8, 8, 3],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 3, 3, 6, 3, 3, 5, 5, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3],
]

#with open('lvl1.pkl', 'wb') as f:
#   pickle.dump(lvl1, f)
#
#with open('lvl2.pkl', 'wb') as f:
#   pickle.dump(lvl2, f)

lava_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
void_group = pygame.sprite.Group()
door_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lever_group = pygame.sprite.Group()


#map
level = open(f'lvl{level_num}.pkl', 'rb')
cmap = pickle.load(level)
newmap = CreateWorld(cmap)


player1 = Playing_entity_one(block_sz + 1, screen_height - 58)
player2 = Playing_entity_two(block_sz + 1, screen_height - 158)

exit_b = Buttons(screen_width / 2 - 200, screen_height / 2, exit_img)
restart_b = Buttons(screen_width / 2 - res_img.get_width() / 2 + 150, screen_height / 2, res_img)
start_b = Buttons(screen_width / 2 - start_img.get_width() / 2 + 150, screen_height / 2, start_img)

# Game Itself
run = True
while run:
    clock.tick(fps)

    screen.blit(bg_img, (0, 0))
    if menu:
        if start_b.screen():
            menu = False

        if exit_b.screen():
            run = False

    elif not menu:
        newmap.drawmap()

        gm_ov = player1.update(gm_ov)
        gm_ov = player2.update(gm_ov)

        lava_group.draw(screen)
        water_group.draw(screen)
        void_group.draw(screen)
        door_group.draw(screen)
        platform_group.draw(screen)
        lever_group.draw(screen)


        if gm_ov == 0:
            lever_state = 0

            if pygame.sprite.spritecollide(player1, water_group, False) or pygame.sprite.spritecollide(player1, void_group, False):
                gm_ov = -1

            if pygame.sprite.spritecollide(player2, lava_group, False) or pygame.sprite.spritecollide(player2, void_group, False):
                gm_ov = -1

            if pygame.sprite.spritecollide(player1, door_group, False) and pygame.sprite.spritecollide(player2, door_group, False):
                gm_ov = 1

            if pygame.sprite.spritecollide(player1, lever_group, False):
                lever_state = 1

            if pygame.sprite.spritecollide(player2, lever_group, False):
                lever_state = 1

            if lever_state == 1:
                lever_group.update()
                platform_group.update()

            else:
                lever_group.update()

        if gm_ov == -1:
            if exit_b.screen():
                run = False

            if restart_b.screen():
                level_num = 1
                cmap = []
                newmap = reset_lvl(level_num)
                gm_ov = 0

        if gm_ov == 1 and level_num != max_level + 1:
            level_num += 1

            if level_num <= max_level:
                cmap = []
                newmap = reset_lvl(level_num)
                gm_ov = 0
            else:
                level_num = 1
                cmap = []
                newmap = reset_lvl(level_num)
                gm_ov = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()

#input()