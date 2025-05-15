# Holds objects that will make up the game.
# Except Players, which are held in a different file
# to reduce file size

import pygame
import math
import Utilities as utl
from collections import deque
# How the LevelSprites class will be used to
# hold the sprites in the game is undecided.
# Possibility 1:
#  Each level has their own LevelSprites instance
#  that CurrentGroup is set to and main.py
#  uses that to update/draw the sprites.
#  This would allow the pause menu to simply
#  be its own level, holding a reference to the
#  previous level/its sprites in order to keep
#  them there but unmoving. This choice might
#  make it easier to have a Level class
#  (or meta/super class) and have those determine how
#  the level loads and interacts with other levels.
#  Another upside to this choice is that it is
#  expandable, and can allow any other sort of menu
#  that might be needed.
#
# Possibility 2:
#  There is one LevelSprites instance that is reused
#  for each level. This would mean that a separate
#  instance would have to be created for the pause
#  menu, and the pause menu  would have its own loop
#  and method to be called inside of main.py. This
#  would mean that each menu would have to have their
#  own loop inside main.py (they can share the LevelSprite
#  instance), but levels wouldn't have to work with
#  other levels and store their current states, and
#  then manage reloading them. Another upside
#  is that certain levels wouldn't be able to have
#  a menu created over them (such as the title screen),
#  although an attribute to signal that could be done
#  inside the first option. This would also be much
#  simpler to implement, being half done already.
#
# Possibility 3:
#  Create a new Menu or MenuOverlay class. This hasn't
#  been fully fleshed out, but the idea is to create
#  a new class that would be able to override the
#  curent level without deleting it or affecting it at
#  all.

# Type hint go brrr
CurrentGroup: utl.hlpr.LevelSprites = None


class Wall(utl.Sprite):
    def __init__(self, pone, ptwo, color):
        #utl.Sprite.__init__(self, CurrentGroup)
        super().__init__(CurrentGroup)
        # Wall uses line-based collision
        self.line = utl.mathobjs.Line(pone, ptwo)
        self.rect = self.line.rect
        self.color = color
        self.moveds = deque()
        self.origs = deque()

    def draw(self, screen):
        pygame.draw.line(screen, self.color,
                         self.line.start, self.line.end, 3)
        #self.drawTheRects(screen)

    # For debugging
    def drawTheRects(self, screen):
        for m in self.moveds:
            pygame.draw.rect(screen, utl.red, m)
        while len(self.moveds) > 5:
            self.moveds.popleft()
        for o in self.origs:
            pygame.draw.rect(screen, utl.green, o, 3)
        while len(self.origs) > 5:
            self.origs.popleft()

    # Snaps a point to the position on the wall closest
    # to it.
    def snapPoint(self, p):
        rP = self.line.reflectpoint(p)
        return [(x + y) / 2 for x, y in zip(p, rP)]

    # Like snapPoint, but within the wall's rect.
    def closestPointOnWall(self, p):
        return utl.clamp_to_rect(self.rect, self.snapPoint(p))

    # Returns a new moved Rect that avoids the wall
    def pushRect(self, orig, moved):
        # Avoid side effects
        moved = moved.copy()

        #  Corners take highest priority
        # Checks if player collides with corners of wall
        # instead of the wall itself
        if self.line.colliderect(orig, bounds="outside"):
            # Establishes which direction to push from
            rpos = [0, 0]  # 'relative position'
            rpos[0] = orig.centerx - self.rect.centerx
            rpos[1] = orig.centery - self.rect.centery

            # If corners are collided in x direction
            if abs(rpos[0]) >= abs(rpos[1]):
                # Push to the left or right, towards orig
                if rpos[0] >= 0:
                    # If moved hit the right, push it to right
                    if moved.left < self.rect.right:
                        moved.left = self.rect.right
                else:
                    # If moved hit the left, push it to left
                    if moved.right > self.rect.left:
                        moved.right = self.rect.left

            # If corners are collided in y direction
            if abs(rpos[1]) >= abs(rpos[0]):
                # Push to the top or bottom, towards orig
                if rpos[1] >= 0:
                    # If moved hit the bottom, push it to bottom
                    if moved.top < self.rect.bottom:
                        moved.top = self.rect.bottom
                else:
                    # If moved hit the top, push it to top
                    if moved.bottom > self.rect.top:
                        moved.bottom = self.rect.top
            # Ignore line of wall if moved by corners
            return moved
        # end of corner case code

        # Finds distance from orig to reflected point on wall
        refchange = self.line.reflectpoint(orig.center)
        refchange = (refchange[0] - orig.centerx, refchange[1] - orig.centery)
        # If orig is on the wall, it can't really
        # be known which side of the wall the rect
        # started from.
        if refchange == (0, 0):
            return moved

        # Pushes moved Rect away from on the wall
        # Yes, I did say that correctly
        push = [0, 0]
        pushBy = 4  # Convenience
        # push = [-utl.flatten(refchange[x], pushBy) for x in [0, 1]]

        # We need the signs of refchange to know which
        # direction to push, but not the value.
        push[0] = -utl.flatten(refchange[0], pushBy)
        push[1] = -utl.flatten(refchange[1], pushBy)

        # Uses refchange to find out which corner to push
        cornerRef = utl.getCorner(moved, *refchange)

        # If moved is on the same side as orig, do nothing
        if self.line.side(cornerRef) == self.line.side(orig.center):
            return moved

        # If moved is on the wall, only push it towards orig
        if self.line.side(cornerRef) is None:
            return moved.move(*push)

        # Find closest point on wall to the corner
        newmoved = self.snapPoint(cornerRef)

        # Move corner onto wall
        cornerRef = newmoved
        # Push moved towards orig
        moved.move_ip(*push)

        self.origs.append(orig)
        self.moveds.append(moved)

        # Return the collided Rect
        return moved

    #Unfinished
    # Returns a new moved Circle that avoids the wall
    def pushCirc(self, orig, moved):
        moved = moved.copy()
        if self.line.collidecirc(orig, bounds="outside"):
            print("yo")

            #  I have found a way to do the corner logic
            #  without any edge cases. Also, the corner
            #  case code in pushRect() may not work exactly
            #  like walls would irl, but I don't care.

            # First thing is to find which endpoint
            # of the wall is closer to the circle.
            wp1 = self.line.start
            wp2 = self.line.end
            oc = tuple(orig.center)  # orig.center is a property
            # There could be a quicker way to do this,
            # but whatever.
            wp = wp1 if utl.pointdist_sq(oc, wp1) < utl.pointdist_sq(oc, wp2) else wp2

            # Find the point on the wall's line
            # closest to orig.center.
            # turn point
            tp = self.snapPoint(oc)

            # turn point offset
            tpoff = [oc[x] - tp[x] for x in (0, 1)]
            # new wall point, uncreative name
            nwp = [wp[x] + tpoff[x] - oc[x] for x in (0, 1)]
            # collision point angle
            cpa = utl.atan2(*nwp)
            # The +1 is to push moved slightly away from
            # the wall, similar to pushBy.
            # collision point radius
            cpr = orig.r + 1
            # collision point
            cp = (math.cos(cpa) * cpr, math.sin(cpa) * cpr)
            # What this does is move cp onto self.line.
            # It may not be on the circle, but it isn't
            # that big of an issue.
            cp = [cp[x] - tpoff[x] for x in (0, 1)]
            moved.center = [wp[x] - cp[x] for x in (0, 1)]
    
            return moved
        # End corner logic

        #  Most of the code here was copied from
        #  pushRect(), sue me.

        # Finds distance from orig to reflected point on wall
        refchange = self.line.reflectpoint(orig.center)
        refchange = (refchange[0] - orig.center[0], refchange[1] - orig.center[1])
        # If orig is on the wall, it can't really
        # be known which side of the wall the rect
        # started from.
        if refchange == (0, 0):
            print("on wall")
            return moved

        # Pushes moved Circ away from on the wall
        push = [0, 0]
        pushBy = 4  # Convenience

        # We need the signs of refchange to know which
        # direction to push, but not the value.
        push[0] = -utl.flatten(refchange[0], pushBy)
        push[1] = -utl.flatten(refchange[1], pushBy)

        #  Uses refchange to find the point on the circle
        #  that protrudes the most into the wall, based
        #  on the wall's angle.
        #  This makes it so that when you shift this point
        #  to where it hit the wall, the circle is entirely
        #  behind that point (relative to the wall).
        angle = utl.atan2(*refchange)
        corner = [0, 0]
        corner[0] = moved.r * math.cos(angle)
        corner[1] = moved.r * math.sin(angle)
        cornerVal = [moved.center[x] + corner[x] for x in (0, 1)]
        print("moved:", moved.center)
        print("angle:", math.degrees(angle))
        print("cornerVal:", cornerVal)
        print("orig.center:", orig.center)
        print("side(cornerVal):", self.line.side(cornerVal))
        print("side(orig.center):", self.line.side(orig.center))

        # If moved is on the same side as orig, do nothing
        if self.line.side(cornerVal) == self.line.side(orig.center):
            print(self.line)
            print("same side")
            print()
            return moved

        # If moved is on the wall, only push it towards orig
        if self.line.side(cornerVal) is None:
            return moved.move(*push)

        # Find closest point on wall to the corner
        newmoved = self.snapPoint(cornerVal)

        # Move corner onto wall
        moved.move_ip(*[newmoved[x] - corner[x] - moved.center[x] for x in (0, 1)])
        # Push moved towards orig
        moved.move_ip(*push)

        self.origs.append(orig)
        self.moveds.append(moved)

        # Return the collided Circ
        return moved


class DisplayText(utl.Sprite):
    def __init__(self, coords, size,
                 tcolor=utl.white, bcolor=utl.black):
        super().__init__()
        self.setColors(tcolor, bcolor)
        self.font = pygame.font.Font(None, size)
        # This is the top left corner of the text.
        # To change position, modify this.
        self.rect = pygame.Rect(coords, (0, 0))

    # Easier way to access its position
    @property
    def pos(self):
        return self.rect.topleft

    @pos.setter
    def pos(self, newPos):
        self.rect.topleft = newPos

    # Convenient way to set both colors
    def setColors(self, text, background):
        self.tcol = text
        self.bcol = background

    # I made this after realising how relatively complex
    # it was, and that I needed it multiple times.
    def centerTo(self, targetRect, text):
        self.rect.size = self.font.size(text)
        self.rect.center = targetRect.center

    def update(self, string):
        self.image = self.font.render(string, 0, self.tcol, self.bcol)
        self.rect.size = self.image.get_rect().size


class DisplayVar(DisplayText):
    def __init__(self, coords, size,
                 tcolor=utl.white, bcolor=utl.black):
        super().__init__(coords, size,
                         tcolor, bcolor)
        self.var = None
        self.formatter = "{0}"
        CurrentGroup.add(self)

    # Gets the value specified by self.var
    # from mainGlobals
    def getVal(self):
        # attrPath could be an instance variable
        attrPath = self.var.split(".")
        varRef = utl.mainGlobals.get(attrPath[0], None)
        for a in attrPath[1:]:
            if varRef is None:
                return
            varRef = getattr(varRef, a, None)
        return varRef

    def update(self):
        value = self.getVal()
        strVal = self.formatter.format(value)
        super().update(strVal)


class DisplayString(DisplayText):
    def __init__(self, coords, size,
                 tcolor=utl.white, bcolor=utl.black):
        super().__init__(coords, size,
                         tcolor, bcolor)
        CurrentGroup.add(self)
        self.name = ""

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, newName):
        self._name = newName
        super().update(self._name)

    def centerTo(self, targetRect):
        super().centerTo(targetRect, self.name)

    # Overrides DisplayText.update
    def update(self):
        pass


class Button(utl.Sprite):
    def __init__(self, pos, size, text, textSize=40):
        super().__init__(CurrentGroup)
        # For collision
        self.rect = pygame.Rect(pos, size)
        # For the image
        self.border = pygame.Rect(0, 1, size[0]-2, size[1]-2)
        self.prevMouseState = False
        self.leftMDown = False
        self.image = pygame.Surface(size)
        self.inactiveBg = utl.black
        self.idleBg = pygame.Color(50, 50, 50)
        self.activeBg = pygame.Color(100, 100, 100)
        # Reset name and display
        self.name = text
        self.display = DisplayText((0, 0), textSize)
        # Center display to rect
        self.display.centerTo(self.rect, text)
        # Position display relative to rect.topleft
        newPos = list(self.display.pos)
        newPos[0] -= self.rect.left
        newPos[1] -= self.rect.top
        self.display.pos = newPos
        self.event = utl.newEvent(utl.CHANGELEVEL)

    # The type attribute is immutable, so a separate
    # method is required. This also wipes any already
    # stored attributes on the event.
    def setType(self, eventType):
        self.event = utl.newEvent(eventType)

    def updateMPos(self, mPos):
        self.mPos = mPos

    def updateMPressed(self, mPressed):
        self.leftMDown = mPressed[0]

    def update(self):
        # Set background/text colors
        if self.rect.collidepoint(self.mPos):
            if self.leftMDown:
                self.display.bcol = self.activeBg
            else:
                self.display.bcol = self.idleBg
                # If mouse has just been released,
                # change state
                if self.prevMouseState:
                    utl.postEvent(self.event)
        else:
            self.display.bcol = self.inactiveBg
        self.image.fill(self.display.bcol)
        # Draw border
        pygame.draw.rect(self.image, utl.white, self.border, 2)
        # This is why display.rect.center needed to be
        # relative to rect.topleft
        self.display.update(self.name)
        self.image.blit(self.display.image,
                        self.display.pos)
        self.prevMouseState = self.leftMDown


#Unfinished
class DisplayRect(utl.Sprite):
    def __init__(self, pos, size, border=utl.white, background=utl.black):
        super().__init__(CurrentGroup)
        self.rect = pygame.Rect(pos, size)
        self.border = pygame.Rect(0, 1, size[0]-2, size[1]-2)
        self.image = pygame.Surface(size)
        self.border_c = border
        self.rect_c = background

    def update(self):
        self.image.fill(self.rect_c)
        pygame.draw.rect(self.image, self.border_c, self.border, 2)


# Base class for round shooty bits
class CircleProjectile(utl.Sprite):
    def __init__(self, speed, angle, pos, size, color):
        super().__init__(CurrentGroup)
        # Defines center of projectile
        self.x = pos[0]
        self.y = pos[1]
        # Set angle/speeds based off of angle
        self.Angle = math.radians(angle)
        # Leveraging some pygame builtins
        self.delt = pygame.Vector2()
        self.delt.from_polar((speed, angle))
        # Define area that the projectile takes up
        self.Hit = utl.mathobjs.Circle(pos, size)
        # Make the display of the projectile
        self.image = pygame.Surface((self.Hit.d, self.Hit.d))
        self.image.set_colorkey(utl.black)
        pygame.draw.circle(self.image, color, (self.Hit.r, self.Hit.r), size)

    @property
    def rect(self):
        return self.Hit.get_rect()

    #Unfinished
    # Only to be executed if the projectile was in a wall
    def handleWalls(self):
        # Kills projectile if a wall is hit
        super().kill()

    #Unfinished
    # Move the projectile
    def update(self):
        # Create circ that is moved
        futurecirc = self.Hit.move(*self.delt)
        # Check for collision with walls
        for w in CurrentGroup.get(Wall):
            if self.Hit.colliderect(w.rect):
                futurecirc = w.pushCirc(self.Hit, futurecirc)
                if w.line.collidecirc(self.Hit):
                    self.handleWalls()
        # Eventually utl.boundary will need its own case
        # but this will do for now.
        futurecirc = futurecirc.clamp(utl.boundary)
        if futurecirc != self.Hit.move(*self.delt):
            self.handleWalls()
        self.Hit = futurecirc


#Unfinished
class BasicBall(CircleProjectile):
    # Could make speed/size/color class variables
    def __init__(self, angle, pos):
        super().__init__(10, angle, pos, 10, utl.white)


#Unfinished
class NitroOrb(CircleProjectile):
    # This might not be a good singular projectile
    def __init__(self, angle, pos):
        super().__init__(6, angle, pos, 5, pygame.Color("yellow"))


#Unfinished
class Laser(utl.mathobjs.Line):
    def __init__(self):
        self.start
        self.end
        self.angle


#Unfinished
# Interacts with player to award points
class PointScorer(utl.Sprite):
    pass
