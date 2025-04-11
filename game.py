# Grid-Based Movement in pygame
# Also can be called Tile-based movement
# This script is just a simple demonstration of how to make a player move on a grid in Pygame.
# It does not include a camera, but it might be enough for simple projects
# I don't include image files or animations, that's a whole another story
# You need Pygame 2.1.3dev8 or higher in order for this to work
import pygame
import sys
from spritesheet import SpriteSheet

TILE_SIZE = 32
WINDOW_SIZE = 320

import random


class Apple(pygame.sprite.Sprite):

	def __init__(self, pos):
		super().__init__()

		filename = 'assets/apple.png'
		appleSpritesheet = SpriteSheet(filename)

		self.original_image = appleSpritesheet.image_at((0, 0, 300, 300),
		                                                (0, 0, 0))
		self.image = pygame.transform.scale(self.original_image,
		                                    (TILE_SIZE, TILE_SIZE))

		self.rect = self.image.get_rect()
		self.rect.x = pos[0]
		self.rect.y = pos[1]


class Player(pygame.sprite.Sprite):

	def __init__(self, pos: tuple[int, int], *groups:
	             pygame.sprite.AbstractGroup):
		super().__init__(*groups)
		# The player is just a blue cube the size of our tiles

		filename = 'assets/robot_moving_spritesheet.png'
		robotSpritesheet = SpriteSheet(filename)

		robot_rect = (0, 0, 32, 32)
		self.original_image = robotSpritesheet.image_at(robot_rect, (0, 0, 0))
		self.image = pygame.transform.rotate(self.original_image, 0)

		self.rect = self.image.get_rect(topleft=pos)

		self.direction = pygame.math.Vector2()
		self.pos = pygame.math.Vector2(self.rect.center)
		self.speed = 95

	def get_input(self, direction):
		if direction == 'W':
			self.direction = self.pos + pygame.math.Vector2(0, -TILE_SIZE)
			self.image = pygame.transform.rotate(self.original_image, 0)
		elif direction == 'S':
			self.direction = self.pos + pygame.math.Vector2(0, TILE_SIZE)
			self.image = pygame.transform.rotate(self.original_image, 180)
		elif direction == 'A':
			self.direction = self.pos + pygame.math.Vector2(-TILE_SIZE, 0)
			self.image = pygame.transform.rotate(self.original_image, 90)
		elif direction == 'D':
			self.direction = self.pos + pygame.math.Vector2(TILE_SIZE, 0)
			self.image = pygame.transform.rotate(self.original_image, 270)

	def move(self, dt):
		# Przemieszczamy robota w kierunku, jeśli jest ruch
		if self.direction.magnitude() != 0:
			self.pos = self.pos.move_towards(self.direction, self.speed * dt)

		if self.pos == self.direction:
			if self.pos[0] < 0:
				self.pos[0] = WINDOW_SIZE + TILE_SIZE // 2
				self.direction = self.pos + pygame.math.Vector2(-TILE_SIZE, 0)
			elif self.pos[0] >= WINDOW_SIZE:
				self.pos[0] = -TILE_SIZE // 2
				self.direction = self.pos + pygame.math.Vector2(TILE_SIZE, 0)
			elif self.pos[1] < 0:
				self.pos[1] = WINDOW_SIZE + TILE_SIZE // 2
				self.direction = self.pos + pygame.math.Vector2(0, -TILE_SIZE)
			elif self.pos[1] >= WINDOW_SIZE:
				self.pos[1] = -TILE_SIZE // 2
				self.direction = self.pos + pygame.math.Vector2(0, TILE_SIZE)

		# Ustalamy nową pozycję robota
		self.rect.center = self.pos

	def update(self, dt):
		self.move(dt)


class World:
	"""
		The World class takes care of our World information.

		It contains our player and the current world.
		"""

	def __init__(self, nr_testu):
		self.player = pygame.sprite.GroupSingle()
		self.player_sprite = Player((WINDOW_SIZE // 2, WINDOW_SIZE // 2),
		                            self.player)

		self.apples = pygame.sprite.Group()

		match nr_testu:
			case 1:
				apple = Apple(pos=(WINDOW_SIZE // 2 - 2 * TILE_SIZE, WINDOW_SIZE // 2))
				self.apples.add(apple)
			case 2:
				apple = Apple(pos=(random.randint(0, WINDOW_SIZE // TILE_SIZE - 1) *
				                   TILE_SIZE, WINDOW_SIZE // 2))
				self.apples.add(apple)
			case 3:
				apple = Apple(pos=(WINDOW_SIZE // 2 - 2 * TILE_SIZE, WINDOW_SIZE // 2))
				self.apples.add(apple)
				apple = Apple(pos=(WINDOW_SIZE // 2 + 2 * TILE_SIZE, WINDOW_SIZE // 2))
				self.apples.add(apple)
				apple = Apple(pos=(WINDOW_SIZE // 2, WINDOW_SIZE // 2 - 2 * TILE_SIZE))
				self.apples.add(apple)
			case 4:
				for _ in range(5):
					x = random.randint(0, WINDOW_SIZE // TILE_SIZE - 1) * TILE_SIZE
					y = random.randint(0, WINDOW_SIZE // TILE_SIZE - 1) * TILE_SIZE
					apple = Apple(pos=(x, y))
					self.apples.add(apple)

	def update(self, dt):
		display = pygame.display.get_surface()
		self.player.update(dt)
		self.player.draw(display)
		self.apples.update(
		)  # Zaktualizuj jabłka (choć nie robimy tu zbyt wielu zmian)
		self.apples.draw(display)

		# Sprawdzanie kolizji między graczem a jabłkiem
		for apple in self.apples:
			if self.player.sprite.rect.colliderect(apple.rect):
				apple.kill()  # Zabij jabłko, gdy zostanie zebrane

	def won(self):
		return len(self.apples) == 0


class Game:
	"""
		Initializes pygame and handles events.
		"""

	def __init__(self, input_file, nr_testu):
		pygame.init()
		# Initialized window and set SCALED for large resolution monitors
		self.window = pygame.display.set_mode([WINDOW_SIZE, WINDOW_SIZE],
		                                      pygame.SCALED)
		# Give a title to the window
		pygame.display.set_caption("Grid-Based Movement in Pygame")
		# You need the clock to get deltatime (dt)
		self.clock = pygame.time.Clock()
		self.world = World(nr_testu)
		# Control whether the program is running
		self.running = True
		# Show the Tile grid
		self.show_grid = True

		self.input_file = input_file
		self.input_commands = []
		self.current_command_index = 0
		self.load_commands()

		self.last_time = pygame.time.get_ticks()

		self.game_ended = False

	def draw_grid(self):
		"""
				Draws the grid of tiles. Helps to visualize the grid-based movement.
				:return:
				"""
		rows = int(WINDOW_SIZE / TILE_SIZE)
		display = pygame.display.get_surface()
		gap = TILE_SIZE  # Każda linia ma odstęp równy rozmiarowi tile

		# Rysowanie poziomych linii
		for i in range(rows):
			pygame.draw.line(display, "grey", (0, i * gap), (WINDOW_SIZE, i * gap))

		# Rysowanie pionowych linii
		for j in range(rows):
			pygame.draw.line(display, "grey", (j * gap, 0), (j * gap, WINDOW_SIZE))

	def load_commands(self):
		with open(self.input_file, 'r') as file:
			self.input_commands = [
			    line.strip().upper() for line in file.readlines() if line.strip()
			]

	def update(self, dt):
		self.window.fill("white")

		if self.show_grid:
			self.draw_grid()

		if self.last_time + 1000 < pygame.time.get_ticks():
			self.last_time = pygame.time.get_ticks()
			# print(f"Time: {self.last_time}")

			if self.current_command_index < len(self.input_commands):
				command = self.input_commands[self.current_command_index]
				self.world.player_sprite.get_input(command)  # Ruch robota
				self.world.update(dt)
				self.current_command_index += 1

				print(f"Command: {command}")
			else:
				self.world.player_sprite.direction = pygame.math.Vector2(
				    0, 0)  # Zatrzymaj robota
				self.world.update(dt)
				self.running = False
			# print("No more commands to execute.")
		else:
			self.world.update(dt)

	def run(self):
		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False

			# Pobierz dt i wykonaj update
			dt = self.clock.tick() / 1000
			self.update(dt)
			pygame.display.update()

		if self.world.won():
			print("Gratulacje! Udało ci się zebrać wszystkie jabłka!")
			pygame.time.wait(1000)
		else:
			print("Nie udało się zebrać wszystkich jabłek. :C")
			pygame.time.wait(1000)

		pygame.quit()
		sys.exit()
