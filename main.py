import pygame
import pygame.locals as pgv
# I don't know what witchcraft makes this work,
# but repl.it doesn't like it either.
#from atpublic import install
#install()
import Sprites as spr
import Levels as lev
#import Players as plr
import Utilities as utl
# Start pygame/Create screen
pygame.init()
screech = pygame.display.set_mode(utl.SCREENSIZE)
# Reference to the variables in main.py
mainGlobals = globals()

# Run command: (The default one)
# bash -c polygott-x11-vnc q && DISPLAY=:0 run-project

"""Plans/Ideas:
X Turn Utilities into a package of modules, 
  so it isn't giant. (other files could
  get the same treatment.)
- Change the movement used in the Player and
  Projectile classes so it's possible to change
  the fps without messing things up.
- Laser class. Made from the Line class, would have
  to move around or something. Might happen.
- Make it so players can take damage.
- Make the scoring mechanisms.
- Make the player select screen.
- Come up with an idea for a level selector.
- Find a way to display player health.
  Idea 1: A bar shows up when damaged.
  Idea 2: Player health is shown using a sprite
    in the level.
- Make a grouping class that can manage players scoring.
- Add a debug.py file, so that the globals in main.py
  don't have to be passed to Utilities for the DisplayVar
  class to work. Instead they can be passed to the debug
  file, specifically reserved to show debug things.

  Another possibility is to just rework the DisplayVar
  class so its takes an object (a player, perchance?)
  as part of its instantiation, so mainGlobals isn't needed.
"""

running = True
# Create timer for framerate
ticker = pygame.time.Clock()

# A very important line
lev.initLevels()
# This line will be removed
utl.mainGlobals = mainGlobals

frame = 0

while running:

    # Allow game to be stopped easily
    for event in pygame.event.get():
        if event.type == pgv.KEYDOWN:
            if event.key == pgv.K_ESCAPE:
                running = False
            # The pause menu
            if event.key == pgv.K_6:
                lev.pause()
        elif event.type == utl.CHANGELEVEL:
            lev.updateLevel(event.level)
        elif event.type == utl.CHANGEPLAYLEVEL:
            lev.updatePlayLevel(event.level)
        elif event.type == utl.SETOVERLAY:
            lev.updateOverlay(event.level)
        elif event.type == pgv.QUIT:
            running = False
    # Don't run when not needed
    if not running:
        break

    # Reset screen
    #screech.fill(utl.black)
    screech.blit(utl.background, (0, 0))

    # Update game sprites
    spr.CurrentGroup.update()
    # Draw game sprites
    spr.CurrentGroup.draw(screech)

    frame += 1
    if frame > utl.FPS:
        frame = 0

    ticker.tick(utl.FPS)

    pygame.display.flip()
