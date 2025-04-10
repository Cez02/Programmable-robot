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


class Player(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[int, int], *groups: pygame.sprite.AbstractGroup):
        super().__init__(*groups)
        # The player is just a blue cube the size of our tiles
        # self.image = pygame.surface.Surface((TILE_SIZE, TILE_SIZE))
        
        filename = 'assets/robot_moving_spritesheet.png'
        robotSpritesheet = SpriteSheet(filename)

        robot_rect = (0, 0, 32, 32)
        self.original_image = robotSpritesheet.image_at(robot_rect, (0, 0, 0))
        self.image = self.original_image
        

        self.rect = self.image.get_rect(topleft=pos)
        # self.image.fill("blue")

        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.moving = False
        self.speed = 95

    def get_input(self):
        keys = pygame.key.get_pressed()
        
        # The elifs prevent the player from walking in diagonal. Generally games like
        # Pokémon do not allow that kind of movement, and that's what we're replicating here
        if keys[pygame.K_UP]:
            self.direction = self.pos + pygame.math.Vector2(0, -TILE_SIZE)
            self.moving = True
            self.image = pygame.transform.rotate(self.original_image, 0)
        elif keys[pygame.K_DOWN]:
            self.direction = self.pos + pygame.math.Vector2(0, TILE_SIZE)
            self.moving = True
            self.image = pygame.transform.rotate(self.original_image, 180)
        elif keys[pygame.K_LEFT]:
            self.direction = self.pos + pygame.math.Vector2(-TILE_SIZE, 0)
            self.moving = True
            self.image = pygame.transform.rotate(self.original_image, 90)
        elif keys[pygame.K_RIGHT]:
            self.direction = self.pos + pygame.math.Vector2(TILE_SIZE, 0)
            self.moving = True
            self.image = pygame.transform.rotate(self.original_image, 270)
        else:
            # Reset the direction to (0, 0), otherwise we'd keep walking forever
            self.direction = pygame.math.Vector2()

    def move(self, dt):
        # We'll only move if the direction of movement is not (0, 0), otherwise the 
        # Player will start moving to the left corner of the screen
        if self.direction.magnitude() != 0:
            # Move_towards function is only available in pygame 2.1.3dev8 and later
            # You can perharps do the same thing with pos.lerp(), but I've not tested it
            self.pos = self.pos.move_towards(self.direction, self.speed * dt)
        
        # Will only stop moving once the position reaches the destination
        if self.pos == self.direction:
            self.moving = False
        
        # You need to point the rect to the position, otherwise it will not appear to move at all
        self.rect.center = self.pos

    def update(self, dt):
        # The player does not respond to input until it reaches the tile destination
        # That is the key to the Grid-Based movement here. If it could respond, then it would walk all over the place
        if not self.moving:
            self.get_input()
        
        # Player keeps moving even without input
        self.move(dt)


class World:
    """
    The World class takes care of our World information.

    It contains our player and the current world.
    """
    def __init__(self):
        self.player = pygame.sprite.GroupSingle()
        Player((0, 0), self.player)

    def update(self, dt):
        display = pygame.display.get_surface()
        self.player.update(dt)
        self.player.draw(display)

# We don't need a class, but it helps organize our code better
class Game:
    """
    Initializes pygame and handles events.
    """
    def __init__(self):
        pygame.init()
        # Initialized window and set SCALED for large resolution monitors
        self.window = pygame.display.set_mode([WINDOW_SIZE, WINDOW_SIZE], pygame.SCALED)
        # Give a title to the window
        pygame.display.set_caption("Grid-Based Movement in Pygame")
        # You need the clock to get deltatime (dt)
        self.clock = pygame.time.Clock()
        self.world = World()
        # Control whether the program is running
        self.running = True
        # Show the Tile grid
        self.show_grid = True

        # filename = 'assets/robot_moving_spritesheet.png'
        # piece_ss = SpriteSheet(filename)

        # # Create a black king.
        # robot_rect = (0, 0, 32, 32)
        # self.robot_img = piece_ss.image_at(robot_rect)

        # self.all_sprites = pygame.sprite.Group()
        # self.all_sprites.add(player)


    @staticmethod
    def draw_grid():
        """
        Draws the grid of tiles. Helps to visualize the grid-based movement.
        :return:
        """
        rows = int(WINDOW_SIZE / TILE_SIZE)
        display = pygame.display.get_surface()
        gap = WINDOW_SIZE // rows
        # for i in range(rows):
        #     pygame.draw.line(display, "grey", (0, i * gap), (WINDOW_SIZE, i * gap))
        #     for j in range(rows):
        #         pygame.draw.line(display, "grey", (j * gap, 0), (j * gap, WINDOW_SIZE))

    def update(self, dt):
        self.window.fill("white")
        
        # self.rect = self.image.get_rect()
        # self.rect.topleft = self.x, self.y
        # self.screen.blit(self.image, self.rect)

        self.world.update(dt)
        if self.show_grid:
            self.draw_grid()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.K_d:  # toggles the grid
                    self.show_grid = not self.show_grid

            # Get deltatime for framerate independence
            dt = self.clock.tick() / 1000
            # Update game logic
            self.update(dt)
            # Similar to display.flip()
            pygame.display.update()

        pygame.quit()
        sys.exit()  # helps quit out of IDLE


if __name__ == "__main__":
    game = Game()
    game.run()
