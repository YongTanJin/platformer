# Import ไลบรารีและโมดูลที่จำเป็น
import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path

# ทำการ initialize Pygame และเซ็ตค่าการแสดงผล
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

# กำหนดพารามิเตอร์ของหน้าจอแสดงผล
clock = pygame.time.Clock()
fps = 60

screen_width = 800
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Escape From Dino')


# กำหนดฟอนต์
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)


#กำหนดตัวแปรเกม
tile_size = 50
game_over = 0
main_menu = True
level = 0
max_levels = 7
score = 0
# ในส่วนต้นทางบน (Top part) ของโค้ด
release_timer = 0
release_delay = 3 # เวลาที่ต้องการจับไว้ก่อนที่จะปล่อยมอนสเตอร์ (หน่วย: วินาที)

# กำหนดสี
white = (255, 255, 255)
blue = (0, 0, 255)


# โหลดรูปภาพและเสียง
sun_img = pygame.image.load('img/sun.png') # ดวงอาทิ
bg_img = pygame.image.load('img/fo.png') # พื้นหลัง
restart_img = pygame.image.load('img/restart_btn.png') #ปุ่มรี
start_img = pygame.image.load('img/start_btn.png') # ปุ่มเริ่ม
exit_img = pygame.image.load('img/exit_btn.png') # ปุ่มออก
how_to_play_img = pygame.image.load("img/how_to_play_btn.png")
back_img = pygame.image.load("img/back_btn.png")
logo_img = pygame.image.load("img/logo.png")
sky_img = pygame.image.load("img/sky.png")

#load sounds
pygame.mixer.music.load('img/music.wav') # เสียงในเกม
pygame.mixer.music.play(-1, 0.0, 5000)
coin_fx = pygame.mixer.Sound('img/coin.wav') # เสียงเหรีญน
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('img/jump.wav') # เสียงกระโดด
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('img/game_over.wav') # เสียงตอนคาย
game_over_fx.set_volume(0.5)

# กำหนดฟังก์ชัน
def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))


#ฟังก์ชั่นเพื่อรีเซ็ตระดับ
def reset_level(level):
  player.reset(100, screen_height - 130)
  blob_group.empty()
  lava_group.empty()
  exit_group.empty()

#โหลดข้อมูลระดับและสร้างโลก
  if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
  world = World(world_data)

  return world

# กำหนดคลาสปุ่ม
class Button():
  def __init__(self, x, y, image):
    self.image = image
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.clicked = False

  def draw(self):
    action = False

    #รับตำแหน่งเมาส์
    pos = pygame.mouse.get_pos()

    #ตรวจสอบตำแหน่งเมาส์และสร้างเงื่อนไขการคลิก
    if self.rect.collidepoint(pos):
      if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
        action = True
        self.clicked = True

    if pygame.mouse.get_pressed()[0] == 0:
      self.clicked = False


    #ปุ่มวาด
    screen.blit(self.image, self.rect)

    return action

# กำหนดคลาสผู้เล่น
class Player():
  def __init__(self, x, y):
    self.reset(x, y)


# กำหนดคลาสอัพเดท
  def update(self, game_over):
    dx = 0
    dy = 0
    walk_cooldown = 5

    if game_over == 0:
      #รับกด
      key = pygame.key.get_pressed()
      if key[pygame.K_SPACE] and self.jumped == False and self.jump_count < 2:
        jump_fx.play()
        self.vel_y = -15
        self.jumped = True
        self.jump_count += 1
      elif self.in_air == False:
        self.jump_count = 0
      if key[pygame.K_SPACE] == False:
        self.jumped = False
      if key[pygame.K_LEFT]:
        dx -= 5
        self.counter += 1
        self.direction = -1
      if key[pygame.K_RIGHT]:
        dx += 5
        self.counter += 1
        self.direction = 1
      if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
        self.counter = 0
        self.index = 0
        if self.direction == 1:
          self.image = self.images_right[self.index]
        if self.direction == -1:
          self.image = self.images_left[self.index]

      #อนิเมชั่นเดินซ้ายขวา
      if self.counter > walk_cooldown:
        self.counter = 0   
        self.index += 1
        if self.index >= len(self.images_right):
          self.index = 0
        if self.direction == 1:
          self.image = self.images_right[self.index]
        if self.direction == -1:
          self.image = self.images_left[self.index]


     #เพิ่มแรงโน้มถ่วง
      self.vel_y += 1
      if self.vel_y > 10:
        self.vel_y = 10
      dy += self.vel_y

      #ตรวจสอบการชน
      self.in_air = True
      for tile in world.tile_list:
        #ตรวจสอบการชนในทิศทาง x
        if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
          dx = 0
        #ตรวจสอบการชนในทิศทาง y
        if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
          #ตรวจดูว่าอยู่ต่ำกว่าพื้นหรือไม่ เช่น กระโดด
          if self.vel_y < 0:
            dy = tile[1].bottom - self.rect.top
            self.vel_y = 0
          #ตรวจสอบว่าอยู่เหนือพื้นดินหรือไม่ เช่น ล้ม
          elif self.vel_y >= 0:
            dy = tile[1].top - self.rect.bottom
            self.vel_y = 0
            self.in_air = False


      #ตรวจสอบการชนกับศัตรู
      if pygame.sprite.spritecollide(self, blob_group, False):
        game_over = -1
        game_over_fx.play()

      #ตรวจสอบการชนกับลาวา
      if pygame.sprite.spritecollide(self, lava_group, False):
        game_over = -1
        game_over_fx.play()

      #ตรวจสอบการชนกับทางออก
      if pygame.sprite.spritecollide(self, exit_group, False):
        game_over = 1


      #อัพเดทพิกัดผู้เล่น
      self.rect.x += dx
      self.rect.y += dy


    elif game_over == -1:
      self.image = self.dead_image
      draw_text('GAME OVER!', font , blue, (screen_width // 2) - 150, screen_height // 2)
      if self.rect.y > 200:
        self.rect.y -= 5

    #วาดเครื่องเล่นลงบนหน้าจอ
    screen.blit(self.image, self.rect)
    pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
    
    return game_over

#กำหนดคลาสผู้เล่น
  def reset(self, x, y):
    self.images_right = []
    self.images_left = []
    self.index = 0
    self.counter = 0
    for num in range(1, 5):
      img_right = pygame.image.load(f'img/w{num}.png')
      img_right = pygame.transform.scale(img_right, (40, 80))
      img_left = pygame.transform.flip(img_right, True, False)
      self.images_right.append(img_right)
      self.images_left.append(img_left)
    self.dead_image = pygame.image.load('img/ghost.png')
    self.image = self.images_right[self.index]
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.width = self.image.get_width()
    self.height = self.image.get_height()
    self.vel_y = 0
    self.jumped = False
    self.direction = 0
    self.in_air = True
    self.jump_count = 0


# กำหนดคลาสโลก
class World():
  def __init__(self, data):
    self.tile_list = []

    #โหลดภาพ
    dirt_img = pygame.image.load('img/dirt.png') #บล็อกดิน
    grass_img = pygame.image.load('img/grass.png') #บล็อกหญ้า

    row_count = 0
    for row in data:
      col_count = 0
      for tile in row:
        if tile == 1:
          img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
          img_rect = img.get_rect()
          img_rect.x = col_count * tile_size
          img_rect.y = row_count * tile_size
          tile = (img, img_rect)
          self.tile_list.append(tile)
        if tile == 2:
          img = pygame.transform.scale(grass_img, (tile_size, tile_size))
          img_rect = img.get_rect()
          img_rect.x = col_count * tile_size
          img_rect.y = row_count * tile_size
          tile = (img, img_rect)
          self.tile_list.append(tile)
        if tile == 3:
          blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
          blob_group.add(blob)
        if tile == 6:
          lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
          lava_group.add(lava)
        if tile == 7:
          coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
          coin_group.add(coin)
        if tile == 8:
          exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
          exit_group.add(exit)
        col_count += 1
      row_count += 1


  def draw(self):
    for tile in self.tile_list:
      screen.blit(tile[0], tile[1])
      pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)


# กำหนดคลาสศัตรู (Monster, Lava, Coin, Exit)
class Enemy(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.image.load('img/dino.png')
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.move_direction = 1
    self.move_counter = 0

  def update(self):
    self.rect.x += self.move_direction
    self.move_counter += 1
    if abs(self.move_counter) > 50:
      self.move_direction *= -1
      self.move_counter *= -1

# กำหนดคลาสศัตรู  Lava
class Lava(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    img = pygame.image.load('img/lava.png')
    self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y

# กำหนดคลาสศัตรู  Coin
class Coin(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    img = pygame.image.load('img/coin.png')
    self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)

# กำหนดคลาสศัตรู Exit
class Exit(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    img = pygame.image.load('img/exit.png')
    self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y

# กำหนดคลาสศัตรู Monster
class Monster(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.transform.scale(pygame.image.load('img/blob1.png'), (int(tile_size * 0.75), tile_size))
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.move_direction = 1
    self.move_counter = 0
    self.chase_timer = 0
    self.chase_duration = 60 # 3 วินาที * 60 เฟรมต่อวินาที
    self.player = None # เพิ่มตัวแปร player

# กำหนดคลาสอัพเดทศัตรู 
def update(self):
    self.rect.x += self.move_direction
    self.move_counter += 1

    if abs(self.move_counter) > 50:
      self.move_direction *= -1
      self.move_counter *= -1

    if self.chase_timer < self.chase_duration and self.player is not None:
      self.chase_timer += 1
    else:
      player_distance = abs(self.rect.x - self.player.rect.x)
      if player_distance < 300:
        if self.rect.x < self.player.rect.x:
          self.move_direction = 1
        elif self.rect.x > self.player.rect.x:
          self.move_direction = -1
      else:
        self.move_direction *= -1
        self.chase_timer = 0 # รีเซ็ตเวลาไล่ล่าเมื่อไม่ได้ไล่ล่า

class HowToPlayScreen: #สร้างหน้า how to play
    def __init__(self):
        self.font = pygame.font.SysFont('Bauhaus 39', 40)
        self.instructions = [
            "How to Play:",
            "1. Use the arrow keys to move left and right.",
            "2. Press SPACE to jump.",
            "3. Press SPACE again for a double jump.",
            "4. Avoid Lava and Dino to reach the end!",
            "press X at top rigth to get back to menu"
        ]
        
    def display(self, screen): #สร้างหน้าจอถมขาวให้วาง text
        screen.fill((255, 255, 255))  # Fill the screen with white background
        y_offset = 50
        for line in self.instructions:
            text = self.font.render(line, True, (0, 0, 0))
            screen.blit(text, (50, y_offset))
            y_offset += 30
        
    def run(self, screen): #ลูปหลักสำหรับการรันหน้าhow to play
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        running = False

            self.display(screen)
            pygame.display.flip()

        return
      
# กำหนดผู้เล่นและกลุ่มสไปรต์เริ่มต้น
player = Player(100, screen_height - 130)

blob_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
monster_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
how_to_play_screen = HowToPlayScreen()


#create dummy coin for showing the score
score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

# โหลดข้อมูลเลเวลและสร้างโลกเริ่มต้น
if path.exists(f'level{level}_data'):
  pickle_in = open(f'level{level}_data', 'rb')
  world_data = pickle.load(pickle_in)
world = World(world_data)


# สร้างปุ่ม
restart_button = Button(screen_width // 2 - 100, screen_height // 2 + 100, restart_img)
back_button = Button(screen_width // 2 + 50, screen_height // 2 + 100, back_img) #รอใส่
start_button = Button(screen_width // 2 - 390, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)
how_to_play_button = Button(screen_width // 2 - 30, screen_height // 2 + 50, how_to_play_img) #รอรูป

sky_rect = sky_img.get_rect(topleft=(0, 0))
sky_rect2 = sky_img.get_rect(topleft=(screen_width, 0))
scroll_speed = 1

# ลูปเกมหลัก
run = True
while run:
  clock.tick(fps)

  screen.blit(bg_img, (0, 0))
  screen.blit(sun_img, (100, 100))
  sky_rect.x -= scroll_speed
  sky_rect2.x -= scroll_speed
  if sky_rect.right <= 0:
    sky_rect.x = 0
  if sky_rect2.right <= 0:
    sky_rect2.x = 0
  screen.blit(sky_img, sky_rect)
  screen.blit(sky_img, sky_rect2)
  
  if main_menu == True:
      # หน้าจอหลัก
    screen.blit(logo_img, (250,100))
    if exit_button.draw():
      run = False
    if start_button.draw():
      level = 0
      score = 0
      world_data = []
      world = reset_level(level)
      game_over = 0
      main_menu = False
    if how_to_play_button.draw():
      how_to_play_screen.run(screen)
      
  else:
    world.draw()

    release_timer += 1
    if release_timer >= release_delay * fps:
      # ปล่อยมอนสเตอร์ในระยะเวลาที่กำหนด
      monster = Monster(0, screen_height - 130)
      monster.player = player # ตรวจสอบว่า player ถูกกำหนดค่าไว้อย่างถูกต้อง
      monster_group.add(monster)
      release_timer = 0


    if game_over == 0:
      # อัพเดทองค์ประกอบของเกม ตรวจสอบการชน และวาดคะแนน
      blob_group.update()
      monster_group.update()
      #อัพเดตคะแนน
      # ตรวจสอบว่ามีการรวบรวมเหรียญหรือไม่
      if pygame.sprite.spritecollide(player, coin_group, True):
        score += 1
        coin_fx.play()
      draw_text('X ' + str(score), font_score, white, tile_size - 10, 10)

    blob_group.draw(screen)
    lava_group.draw(screen)
    coin_group.draw(screen)
    monster_group.draw(screen)
    exit_group.draw(screen)

    game_over = player.update(game_over)

    # ตรวจสอบว่าผู้เล่นตายหรือไม่
    if game_over == -1:
      if restart_button.draw():
        world_data = []
        world = reset_level(level)
        game_over = 0
        score = 0
      if back_button.draw():
        main_menu = True
        
    # ตรวจสอบว่าผู้เล่นได้ผ่านเลเวลหรือไม่
    if game_over == 1:
      # ถ้าผู้เล่นชนะ แสดงข้อความและให้เลือกเริ่มใหม่
      level += 1
      if level <= max_levels:
        # reset level
        world_data = []
        world = reset_level(level)
        game_over = 0
      else:
        draw_text('YOU WIN!', font, blue, (screen_width // 2) - 140, screen_height // 2)
        if restart_button.draw():
          level = 0
          # reset level
          world_data = []
          world = reset_level(level)
          game_over = 0
          score = 0

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False

  pygame.display.update()

pygame.quit()