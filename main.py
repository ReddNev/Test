import random

import pygame

pygame.init()

screen_title = 'PacMan'
screen_width = 1280
screen_height = 720
screen_color = (200, 200, 200)
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption(screen_title)

fps = 60
clock = pygame.time.Clock()

class Game():

	def __init__(self):
		self.is_working = False

	def start_game(self):
		self.is_working = True

	def stop_game(self):
		self.is_working = False

	def debug_info(self):
		print('FPS:', round(clock.get_fps(), 2))


class Hitbox():

	def __init__(self, x, y, width, height, hitbox_size, hitbox_color):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.hitbox_size = hitbox_size
		self.hitbox_color = hitbox_color

		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

	def draw_hitbox(self):
		pygame.draw.rect(screen, self.hitbox_color, self.rect, self.hitbox_size)


class Model(Hitbox):

	def __init__(self, x, y, width, height, hitbox_size, hitbox_color, img_url):
		Hitbox.__init__(self, x, y, width, height, hitbox_size, hitbox_color)
		self.image = pygame.transform.scale(pygame.image.load(img_url).convert_alpha(), (self.width, self.height))

	def draw_model(self):
		screen.blit(self.image, (self.rect.x, self.rect.y))


class Creature(Model):

	def __init__(self, x, y, width, height, hitbox_size, hitbox_color, img_url, speed):
		Model.__init__(self, x, y, width, height, hitbox_size, hitbox_color, img_url)
		
		self.speed = speed
		
		self.dx = 0
		self.dy = 0

		self.direction = 'idle'
		self.animation_count = 0
		self.frame = 0

	def setup_animation(self, frame_list, animation_delay):
		self.animation_delay = animation_delay
		self.frames = {'left': [], 'right': [], 'up': [], 'down': []}
		for i in range(len(frame_list)):
			current_frame = pygame.transform.scale(pygame.image.load(frame_list[i]).convert_alpha(), (self.width, self.height))
			self.frames['left'].append(pygame.transform.rotate(current_frame, 180))
			self.frames['right'].append(current_frame)
			self.frames['up'].append(pygame.transform.rotate(current_frame, 90))
			self.frames['down'].append(pygame.transform.rotate(current_frame, -90))

	def animation(self):
		if self.direction != 'idle':
			if self.animation_count == fps / self.animation_delay:
				self.animation_count = 0
				self.image = self.frames[self.direction][self.frame]
				if self.frame == len(self.frames[self.direction]) - 1:
					self.frame = 0
				else:
					self.frame += 1
			else:
				self.animation_count += 1

	def move(self):
		self.rect.x += self.dx * self.speed
		self.rect.y += self.dy * self.speed

	def collide_screen(self):
		if self.rect.left < 0:
			self.rect.left = 0
		elif self.rect.right > screen_width:
			self.rect.right = screen_width

		if self.rect.top < 0:
			self.rect.top = 0
		elif self.rect.bottom > screen_height:
			self.rect.bottom = screen_height


class Enemy(Creature):

	def setup_movement(self, movement_delay):
		self.movement_delay = movement_delay
		self.movement_count = fps * self.movement_delay

	def change_direction(self):
		if self.movement_count == fps * self.movement_delay:
			self.movement_count = 0
			directions = ['left', 'right', 'up', 'down']
			if self.direction in directions:
				directions.remove(self.direction)
			self.direction = random.choice(directions)
			if self.direction == 'left':
				self.dx = -1
				self.dy = 0
			elif self.direction == 'right':
				self.dx = 1
				self.dy = 0
			elif self.direction == 'up':
				self.dx = 0
				self.dy = -1
			elif self.direction == 'down':
				self.dx = 0
				self.dy = 1
		else:
			self.movement_count += 1


class Pacman(Creature):

	def controller(self):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_a] and not keys[pygame.K_d]:
			self.dx = -1
			self.dy = 0
			self.direction = 'left'
		elif keys[pygame.K_d] and not keys[pygame.K_a]:
			self.dx = 1
			self.dy = 0
			self.direction = 'right'

		if keys[pygame.K_w] and not keys[pygame.K_s]:
			self.dy = -1
			self.dx = 0
			self.direction = 'up'
		elif keys[pygame.K_s] and not keys[pygame.K_w]:
			self.dy = 1
			self.dx = 0
			self.direction = 'down'

	def collide_enemies(self, sprite_list):
		for sprite in sprite_list:
			if self.rect.colliderect(sprite.rect):
				sprite_list.remove(sprite)
		return sprite_list

pacman = Pacman(0, 0, 64, 64, 1, (255, 0, 0), 'pacman1.png', 5)
pacman.rect.center = (screen_width // 2, screen_height // 2)
pacman.setup_animation(['pacman1.png', 'pacman2.png', 'pacman3.png'], 10)

def spawn_enemies():
	enemies = list()
	for i in range(4):
		enemy = Enemy(random.randint(100, screen_width - 164), random.randint(100, screen_height - 164), 64, 64, 1, (255, 0, 0), 'enemy1.png', 2)
		enemy.setup_animation(['enemy1.png', 'enemy2.png', 'enemy3.png'], 5)
		enemy.setup_movement(5)
		enemies.append(enemy)
	return enemies

enemies = spawn_enemies()

game = Game()
game.start_game()

while game.is_working:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			game.stop_game()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_q:
				game.stop_game()
			if event.key == pygame.K_i:
				game.debug_info()

	screen.fill(screen_color)

	pacman.controller()
	pacman.move()
	pacman.collide_screen()
	pacman.animation()
	pacman.draw_model()
	enemies = pacman.collide_enemies(enemies)

	for enemy in enemies:
		enemy.move()
		enemy.change_direction()
		enemy.collide_screen()
		enemy.animation()
		enemy.draw_model()

	if len(enemies) == 0:
		enemies = spawn_enemies()

	pygame.display.update()
	clock.tick(fps)