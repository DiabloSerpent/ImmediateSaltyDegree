# Holds levels/their contents

import Sprites as spr
import Utilities as utl
import Players as plr
import pygame.locals as pgv
from pygame import Color

currentLevel = None
currentOverlay = None

# This is the level that is loaded when play is pressed
playLevel = None


AMT_PLAYERS = 2
#  Since there are only 2 players, I figured it would
#  easier for them to have their own variables.
# Create player handlers
R = plr.PlayerHandler(utl.red)
B = plr.PlayerHandler(utl.blue)
R.playCharacter = plr.Basic
B.playCharacter = plr.Bill
# ((pgv.K_w, pgv.K_s, pgv.K_a, pgv.K_d), pgv.K_q, pgv.K_e)
R.movekeys = (pgv.K_w, pgv.K_s, pgv.K_a, pgv.K_d)
R.proj_key = pgv.K_q
R.spec_key = pgv.K_e
# ((pgv.K_i, pgv.K_k, pgv.K_j, pgv.K_l), pgv.K_o, pgv.K_u)
B.movekeys = (pgv.K_i, pgv.K_k, pgv.K_j, pgv.K_l)
B.proj_key = pgv.K_o
B.spec_key = pgv.K_u


"""def init():
    initLevels()"""


def initLevels():
    global currentLevel
    # This is here so currentLevel has an unload method
    currentLevel = Level()
    utl.postNewEvent(utl.CHANGELEVEL, level=MainMenu)
    utl.postNewEvent(utl.CHANGEPLAYLEVEL, level=Test)


class Level:
    def __init__(self, amtPlayers=0):
        self.override = 0
        self.isOverlay = False
        self.isGameplay = False
        #self.plyr = defaultdict(utl.hlpr.AttrCollector)
        self.plyr = [utl.hlpr.AttrCollector() for _ in range(amtPlayers)]
        self.sprites = utl.hlpr.LevelSprites()
        self.loadObjects = lambda: None

    def loader(self, loadFunc):
        self.loadObjects = loadFunc
        return loadFunc

    def initPlayers(self):
        for plyr, handler in zip(self.plyr, plr.Handlers):
            for a, v in plyr.__dict__.items():
                setattr(handler, a, v)

    def load(self):
        self.loadObjects()
        if len(self.plyr) > 0:
            self.initPlayers()
            createPlayers()

    def unload(self):
        self.sprites.empty()
        if len(self.plyr) > 0:
            deletePlayers()


class Menu(Level):
    def __init__(self):
        super().__init__()
        self.override = 2


class Overlay(Level):
    def __init__(self):
        super().__init__()
        self.override = 1
        self.isOverlay = True


class Gameplay(Level):
    def __init__(self, amtPlayers=2):
        super().__init__(amtPlayers)
        self.isGameplay = True


# Updates the level when a utl.CHANGELEVEL
# event occurs
def updateLevel(newLevel):
    global currentLevel, currentOverlay
    if type(newLevel) is str:
        newLevel = globals()[newLevel]

    if not isinstance(newLevel, Level):
        raise TypeError(f"{newLevel} is not a Level")

    if newLevel is not currentLevel:
        removeCurrentOverlay()

        currentLevel.unload()
        spr.CurrentGroup = newLevel.sprites
        newLevel.load()
        currentLevel = newLevel


def updatePlayLevel(newLevel):
    global playLevel
    if type(newLevel) is str:
        newLevel = globals()[newLevel]
    playLevel = newLevel


def updateOverlay(newOverlay):
    global currentOverlay, currentLevel
    removeCurrentOverlay()
    print("current:", currentLevel)
    print("new:", newOverlay)

    if newOverlay is None:
        return
    elif currentLevel.override > newOverlay.override:
        return

    if not isinstance(newOverlay, Level):
        raise TypeError(f"{newOverlay} is not a level")

    if newOverlay is not currentOverlay:
        spr.CurrentGroup.draw(utl.background)
        spr.CurrentGroup = newOverlay.sprites
        newOverlay.load()
        currentOverlay = newOverlay


def removeCurrentOverlay():
    global currentOverlay, currentLevel
    if currentOverlay is not None:
        currentOverlay.unload()
        currentOverlay = None
    spr.CurrentGroup = currentLevel.sprites
    utl.resetBackground()


def pause():
    if currentOverlay is not PauseMenu:
        utl.postNewEvent(utl.SETOVERLAY, level=PauseMenu)
    else:
        utl.postNewEvent(utl.SETOVERLAY, level=None)


# Assign the player variables to the
# correct characters.
def createPlayers():
    for ph in plr.Handlers:
        ph.createPlayer()


# Reset the players to None
def deletePlayers():
    for ph in plr.Handlers:
        ph.clearPlayer()


# Creates multiple walls connected to each other using
# a list of points and a color
def multiLineWall(pList, color):
    for s, e in zip(pList[0:], pList[1:]):
        spr.Wall(s, e, color)


Test = Level(amtPlayers=2)
Test.plyr[0].startPos = (380, 300)
Test.plyr[1].startPos = (420, 300)
'''#Syntax rework idea:
Test = Gameplay(
    dict(startPos=(380, 300)),
    dict(startPos=(420, 300))
    default={"startPos": utl.boundary.center}
)
'''
'''#Syntax Idea 2: YAML Boogaloo
name: Test
totalPlayers: 2
playerData:
  - spawnPoints: [[380, 300]]
    character: Bill
  - spawnPoints: [[420, 300]]
defaultPlayerData:
  spawnPoints: [[400, 300]]
'''

@Test.loader
def loadTest():
    # The sprites are automatically added to
    # spr.CurrentGroup, so the names are only
    # there to help create them.
    dsv_rx = spr.DisplayVar((500, 50), 50, utl.red)
    dsv_rx.var = "lev.R.player.rect.x"
    dsv_ry = spr.DisplayVar((600, 50), 50, utl.red)
    dsv_ry.var = "lev.R.player.rect.y"
    dsv_bx = spr.DisplayVar((500, 100), 50, utl.blue)
    dsv_bx.var = "lev.B.player.rect.x"
    dsv_by = spr.DisplayVar((600, 100), 50, utl.blue)
    dsv_by.var = "lev.B.player.rect.y"
    dsv_frame = spr.DisplayVar((50, 500), 40)
    dsv_frame.var = "frame"

    dsv_rvx = spr.DisplayVar((50, 350), 40, utl.red)
    dsv_rvx.var = "lev.R.player.deltx"
    dsv_rvx.formatter = "deltX: {0:.4f}"
    dsv_rvy = spr.DisplayVar((50, 400), 40, utl.red)
    dsv_rvy.var = "lev.R.player.delty"
    dsv_rvy.formatter = "deltY: {0:.4f}"

    spr.Wall((500, 300), (600, 300), Color("yellow"))
    #  Walls also automatically add themselves to
    #  spr.CurrentGroup upon creation.
    # Add all of the walls in the level
    spr.Wall((0, 33), (200, 33), utl.red)
    # Showcase multiLineWall
    points = (
        (233, 33), (367, 33), (367, 267), (333, 267),
        (300, 233), (267, 233), (233, 267), (233, 200),
        (333, 200), (333, 133))
    multiLineWall(points, utl.green)
    spr.Wall((267, 133), (367, 133), utl.blue)
    spr.Wall((267, 133), (267, 67),  utl.blue)
    spr.Wall((300, 100), (300, 67),  utl.blue)
    spr.Wall((300, 67),  (333, 67),  utl.blue)
    spr.Wall((0, 100),   (167, 100), utl.blue)
    spr.Wall((167, 100), (167, 133), utl.blue)
    spr.Wall((167, 133), (200, 100), utl.blue)
    spr.Wall((200, 100), (233, 133), utl.blue)
    spr.Wall((233, 133), (200, 167), utl.blue)

    # This is the setup required for a button.
    to_test2 = spr.Button((600, 400), (150, 100), "To Test2")
    to_test2.event.level = Test2
    '''thing = spr.Button((num, num), (num, num), 
                       "Some Words", 67
                       ev_type=utl.CHANGELEVEL)
    thing.event.level = eirghusjkvd'''


# For testing loading separate levels
Test2 = Level(amtPlayers=2)
Test2.plyr[0].startPos = (300, 300)
Test2.plyr[1].startPos = (500, 300)

@Test2.loader
def loadTest2():
    spr.Wall((300, 200), (500, 400), utl.red)
    spr.Wall((300, 400), (500, 200), utl.blue)
    spr.Wall((700, 500), (705, 505), utl.blue)

    test_over = spr.Button((310, 410), (180, 100), "Test Overlay")
    test_over.setType(utl.SETOVERLAY)
    test_over.event.level = TestOverlay


TestOverlay = Overlay()

@TestOverlay.loader
def loadTestOverlay():
    spr.DisplayRect((50, 50), (200, 400), utl.red, utl.black)
    to_test = spr.Button((75, 75), (150, 100), "To Test")
    to_test.event.level = Test
    to_main = spr.Button((75, 200), (150, 100), "To Menu")
    to_main.event.level = MainMenu
    back = spr.Button((75, 325), (150, 100), "Back")
    back.setType(utl.SETOVERLAY)
    back.event.level = None


PauseMenu = Overlay()

@PauseMenu.loader
def loadPause():
    outline = spr.DisplayRect((0, 0), (200, 400))
    outline.rect.center = utl.boundary.center
    xOffset = outline.rect.left + 25
    yOffset = outline.rect.top + 25
    to_main = spr.Button((xOffset, yOffset), (150, 100), "To Menu")
    to_main.event.level = MainMenu
    back = spr.Button((xOffset, yOffset+125), (150, 100), "Back")
    back.setType(utl.SETOVERLAY)
    back.event.level = None
    quit = spr.Button((xOffset, yOffset+250), (150, 100), "Quit")
    quit.setType(pgv.QUIT)


# Where the game starts
MainMenu = Menu()

@MainMenu.loader
def loadMenu():
    # Create title
    title = spr.DisplayString((0, 0), 80, utl.blue, utl.red)
    title.name = "ImmediateSaltyDegree"
    title.centerTo(utl.boundary)
    title.rect.move_ip(0, -200)

    play = spr.Button((0, 0), (200, 80), "Play Game")
    play.rect.center = utl.boundary.center
    play.event.level = "playLevel"
    levels = spr.Button((0, 0), (200, 80), "Levels")
    levels.rect.center = utl.boundary.center
    levels.rect.move_ip(0, 100)
    # The type attribute is immutable, so a separate
    # method is required. This also wipes any already
    # stored attributes.
    levels.setType(utl.CHANGEPLAYLEVEL)
    levels.event.level = Test
    chars = spr.Button((0, 0), (200, 80), "Characters")
    chars.rect.center = utl.boundary.center
    chars.rect.move_ip(0, 200)
    #chars.setType(utl.CHANGEPLAYLEVEL)
    chars.event.level = selectCharacters


selectCharacters = Level(amtPlayers=2)

selectCharacters.plyr[0].startPos = (350, 500)
selectCharacters.plyr[1].startPos = (450, 500)
selectCharacters.plyr[0].character = plr.Selecter
selectCharacters.plyr[1].character = plr.Selecter

@selectCharacters.loader
def loadCharacterSelect():
    back = spr.Button((50, 50), (150, 100), "Menu")
    back.event.level = MainMenu
    title = spr.DisplayString((0, 50), 60)
    title.name = "Select A Character"
    title.rect.centerx = utl.boundary.centerx
    title.rect.move_ip(50, 0)
