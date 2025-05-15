# Holds the different characters of the game
import pygame
import Sprites as spr
import Utilities as utl
# For angle maths
import math

# Easy way to loop through the 4 direction names
# Up, Down, Left, Right
DIRECTIONS = ["U", "D", "L", "R"]

PLAYERSIZE = (20, 20)

Handlers = []


# Used in Levels.py, organizes aspects of a player
# that would be better put in Levels than Players
class PlayerHandler:
    """Holds a few things related to the
    player objects in Levels.py. These aspects
    control how the players are used, and so don't
    fit well within the Player class.

    Attributes
    ----------
     - __player:__ BasePlayer\n
        Holds a reference to the player object
     - __character:__ type\n
        The class type of the player
     - __playCharacter:__ type\n
        The default type of the player, if character
        is not set by a level upon loading.
     - __color:__ pygame.Color\n
        The color the player is created as.
     - __movekeys:__ tuple\n
        A tuple holding the values of the movement keys.
        This is in the order UP, DOWN, LEFT, RIGHT
     - __proj_key:__ int\n
        The value of the projectile key
     - __spec_key:__ int\n
        The value of the special key
     - __startPos:__ tuple\n
        Position that the player's center is
        assigned to upon creation.
    """

    def __init__(self, color):
        Handlers.append(self)
        # The player object
        self.player = None
        # Reference to a player class
        self.character = None
        # Main color of player
        self.color = color
        # Input names of player
        self.movekeys = None
        self.proj_key = None
        self.spec_key = None
        # Starting position of player
        self.startPos = utl.boundary.center
        self.playCharacter = Basic

    def createPlayer(self):
        if self.character is None:
            self.character = self.playCharacter
        self.player = self.character(self.color)
        self.player.setInputs(self.movekeys,
                              self.proj_key,
                              self.spec_key)
        self.player.rect.center = self.startPos
        self.character = None

    def clearPlayer(self):
        self.player = None


# This determines which classes can be selected by
# players of the game.
PlayableTypes = []


# A simple way of getting all of the different
# character types into a list.
def PlayableType(cls):
    PlayableTypes.append(cls)
    return cls


# Base Player class, holds redundant methods for characters.
class BasePlayer(utl.Sprite):
    MAXHEALTH = 100
    def __init__(self, color, *, size=PLAYERSIZE):
        super().__init__(spr.CurrentGroup)
        self.health = 100

        # Holds movement inputs in list
        self.MOVE = {x: 0 for x in DIRECTIONS}
        self.DASH = {x: 0 for x in DIRECTIONS}
        self.dFCounter = {x: 0 for x in DIRECTIONS}
        self.DCombos = {x: None for x in DIRECTIONS}
        self.dFrames = [[2, 12], [2, 10], [1, None]]
        # Extra convenience
        self.hasDash = False
        self.hasMove = False
        self.cooldown = {"P": 100,  # Projectile
                         "S":  60,  # Special
                         "D":  60}  # Dash
        self.oFCounter = [0, 0]
        # Is toggled, Previous input
        self.PROJ = [False, False]
        self.SPEC = [False, False]

        # Used to for firing projectiles
        self.Angle = 0
        self.colors = {"main": color, "line": utl.white}
        # Updates self.color before drawBaseImage is
        # called, to not make it freak out about
        # undefined colors.
        self.updateColors()
        self._baseImage = pygame.Surface(size)
        self.rect = self._baseImage.get_rect()
        self.drawBaseImage()
        self._baseImage.set_colorkey(utl.black)
        self.resetImage()
        # Create speed of player
        self.delty = 0
        self.deltx = 0

    #  Should be called after __init__()
    # Set which keys to take inputs from
    def setInputs(self, movekeys, proj, spec):
        # Used in updateInputs
        # IDs stores all needed button numbers
        self.IDs = dict(zip(DIRECTIONS, movekeys))
        for d in DIRECTIONS:
            self.DCombos[d] = utl.hlpr.KeyCombo(
                self.IDs[d], self.dFrames[0],
                -self.IDs[d], self.dFrames[1],
                self.IDs[d], self.dFrames[2]
            )
        # Add in proj and spec button ids
        self.IDs["P"] = proj
        self.IDs["S"] = spec

    #  This is called in __init__()
    # Meant be overwritten by other character classes,
    # which is why it is in its own method
    def drawBaseImage(self):
        #self._baseImage.fill(self.colors["main"])
        pygame.draw.circle(self._baseImage, self.colors["main"], self.rect.center, 10)

    # Resets image to its base state
    def resetImage(self):
        self.image = self._baseImage.copy()

    #  This is called in __init__(), after self.color
    #  is created.
    # To be overridden by subclasses if needed
    def updateColors(self):
        pass

    @property
    def delt(self):
        return (self.deltx, self.delty)

    @delt.setter
    def delt(self, newDelt):
        self.deltx = newDelt[0]
        self.delty = newDelt[1]

    # Updates the angle to match the current speed
    def updateAngle(self, dx, dy):
        self.Angle = utl.atan2(dx, dy)

    def getAngle(self):
        return math.degrees(self.Angle)

    # Redraw whatever needs to be redrawn
    def updateImage(self):
        pass

    # Simplifies direct key inputs
    def updateKeys(self, keys):

        self.hasMove = False
        #  Set directional input.
        for x in DIRECTIONS:
            self.MOVE[x] = keys[self.IDs[x]]
            if self.MOVE[x]:
                self.hasMove = True

        # Toggle action keys if needed
        pDown = keys[self.IDs["P"]]
        if pDown and not self.PROJ[1]:
            self.PROJ[0] = not self.PROJ[0]
        # Set previous input for next frame
        self.PROJ[1] = pDown

        sDown = keys[self.IDs["S"]]
        if sDown and not self.SPEC[1]:
            self.SPEC[0] = not self.SPEC[0]
        self.SPEC[1] = sDown

        self.hasDash = False
        for d in DIRECTIONS:
            if self.dFCounter[d] > 0:
                self.dFCounter[d] -= 1
                continue
            self.DCombos[d].update(keys)
            self.DASH[d] = self.DCombos[d].hasMatch
            if self.DASH[d]:
                self.hasDash = True

    def update(self):
        # Designed so that the entire method doesn't
        # have to be rewritten for each class, only
        # the needed sections.
        self.MoveAction()
        self.DashAction()
        self.ProjAction()
        self.SpecAction()
        self.resetImage()
        self.updateImage()
        self.doCollision()
        # Players are blocked from going out of bounds
        self.rect.clamp_ip(utl.boundary)

    def doCollision(self):
        # Checks for walls the player might run into.
        origCirc = utl.mathobjs.Circle(self.rect.center, 10)
        futurerect = self.rect.move(self.deltx, self.delty)
        circ = origCirc.move(self.deltx, self.delty)
        moveArea = self.rect.union(futurerect)
        '''closestWall = None
        # The distances can't be lower than 0
        cWallDist = -1'''
        #(x for x in spr.CurrentGroup.get(spw.Wall) if x.rect.colliderect(moveArea))
        for wall in spr.CurrentGroup.get(spr.Wall):
            if wall.rect.colliderect(moveArea):
                '''p = wall.closestPointOnWall(origCirc.center)
                dist = utl.pointdist_sq(origCirc, p)
                if dist > cWallDist:
                    cWallDist = dist
                    closestWall = wall'''
                circ = wall.pushCirc(origCirc, circ)
                #futurerect = wall.pushRect(self.rect, futurerect)
        '''if closestWall is not None:
            circ = closestWall.pushCirc(origCirc, circ)'''
        futurerect = circ.get_rect()

        # Updates speed to match movement
        #origCirc.move(self.deltx, self.delty) != circ
        #self.rect.move(self.deltx, self.delty) != futurerect
        if origCirc.move(self.deltx, self.delty) != circ:
            #print("circ.center:", circ.center)
            #print("futurerect.center:", futurerect.center)
            # Stops movement to help prevent dashing
            # through walls
            self.deltx = 0
            self.delty = 0
            pass
        # Moves player rect/limits to screen
        self.rect = futurerect

    # Does the move key action
    def MoveAction(self):
        # Very fancy movement logic I probably saw in the game jam
        self.delty += (self.MOVE["D"] - self.MOVE["U"])
        self.deltx += (self.MOVE["R"] - self.MOVE["L"])
        self.delty *= 0.85
        self.deltx *= 0.85
        # Cuts off movement below a certain speed
        if abs(self.deltx) < 0.01:
            self.deltx = 0
        if abs(self.delty) < 0.01:
            self.delty = 0
        if self.hasMove:
            self.updateAngle(self.deltx, self.delty)

    # Does the Dash key action
    def DashAction(self):
        pass

    # Does the Projectile action
    def ProjAction(self):
        pass

    # Does the Special action
    def SpecAction(self):
        pass


class Selecter(BasePlayer):
    def __init__(self, color):
        super().__init__(color, size=(40, 40))

    def drawBaseImage(self):
        base = self._baseImage
        img = utl.images["SelectorImg"]
        base.blit(img.surf, (0, 0))
        img.fill_main(base, self.colors["main"])


@PlayableType
class Basic(BasePlayer):
    def updateImage(self):
        utl.draw_line_from_center(
            self.image,
            self.colors["line"],
            self.Angle)

    # Does the Dash key action
    def DashAction(self):
        dashDir = ""
        # Check if a dash is active
        if self.hasDash:
            for x in DIRECTIONS:
                if self.DASH[x]:
                    dashDir = x
                self.dFCounter[x] = self.cooldown["D"]
        if dashDir == "U":
            self.delty = -15
        elif dashDir == "D":
            self.delty = 15
        elif dashDir == "L":
            self.deltx = -15
        elif dashDir == "R":
            self.deltx = 15

    # Does the Projectile action
    def ProjAction(self):
        if self.PROJ[0] or self.oFCounter[0] != 0:
            self.oFCounter[0] += 1
        if self.oFCounter[0] >= self.cooldown["P"]:
            if self.PROJ[0]:
                spr.BasicBall(self.getAngle(), self.rect.center)
            self.oFCounter[0] = 0

# Inspired by Bill Rizer from Contra: Rebirth
@PlayableType
class Bill(BasePlayer):
    def __init__(self, color):
        super().__init__(color)
        self.cooldown["P"] = 10
        self.cooldown["D"] = 0
        # Added to help aim diagonally
        self.angCombiner = [10, 0]
        self.changeAngle = False

    def updateColors(self):
        # Gray for angle indicator
        self.colors["line"] = pygame.Color("darkgrey")
        # Skin tone is from color-hex:
        # https://www.color-hex.com/color-palette/737
        self.colors["skin"] = (255, 205, 148)

    # Draws rectangle of skin with "belt"
    # It also sounds really weird that way
    def drawBaseImage(self):
        super().drawBaseImage()
        area = pygame.Rect(5, 5, 12, 12)
        pygame.draw.rect(self._baseImage, self.colors["skin"], area)

    def updateImage(self):
        utl.draw_line_from_center(
            self.image,
            self.colors["line"],
            self.Angle)

    def MoveAction(self):
        if self.changeAngle:
            # If dashing, change angle
            # Updates "speed" of angle
            self.angCombiner[0] += (self.MOVE["R"] - self.MOVE["L"])
            self.angCombiner[1] += (self.MOVE["D"] - self.MOVE["U"])
            # Caps out speed of angle for easy turning
            self.angCombiner[0] *= 0.85
            self.angCombiner[1] *= 0.85
            # Update/draw the actual angle
            self.updateAngle(*self.angCombiner)
        # else, do normal movement
        else:
            self.deltx += (self.MOVE["R"] - self.MOVE["L"])
            self.delty += (self.MOVE["D"] - self.MOVE["U"])
        # Ensures player stops when not dashing
        self.deltx *= 0.85
        self.delty *= 0.85
        if abs(self.deltx) < 0.01:
            self.deltx = 0
        if abs(self.delty) < 0.01:
            self.delty = 0

    # Ensure you can turn toward all directions
    # even if original dash is cancelled
    def DashAction(self):
        if self.hasDash:
            self.changeAngle = True
        elif self.changeAngle and not self.hasMove:
            self.changeAngle = False
        # One-liner version because why not:
        # self.changeAngle = self.hasDash or (self.changeAngle and self.hasMove)

    def ProjAction(self):
        if self.PROJ[0] or self.oFCounter[0] != 0:
            self.oFCounter[0] += 1
        if self.oFCounter[0] >= self.cooldown["P"]:
            if self.PROJ[0]:
                spr.NitroOrb(self.getAngle(), self.rect.center)
            self.oFCounter[0] = 0
