import pygame
import public

"""@public
def init(p_mainGlobals):
    global mainGlobals
    print("init 1:", mainGlobals)
    mainGlobals = p_mainGlobals
    print("init 2:", mainGlobals)"""


# Define basic colors
public(
white = pygame.Color(255, 255, 255),
black = pygame.Color(0, 0, 0),
blue = pygame.Color(0, 0, 255),
red = pygame.Color(255, 0, 0),
green = pygame.Color(0, 255, 0)
)

public(
SCREENSIZE = (800, 600)
)

# Represents the size of the screen
public(
boundary = pygame.Rect((0, 0), SCREENSIZE)
)


@public
def resetBackground():
    background.fill(black)


# Will be used in main.py to determine what
# is drawn as the background
public(
background = pygame.Surface(SCREENSIZE)
)
resetBackground()
# Reference to globals dict in main.py
public(
mainGlobals = None,
FPS = 60
)

public(
QUITEVENT = pygame.event.Event(pygame.QUIT)
)
# It's a great name, don't judge
CURRENT_LAST_EVENT_TYPE = pygame.USEREVENT


def new_event_type():
    global CURRENT_LAST_EVENT_TYPE
    CURRENT_LAST_EVENT_TYPE += 1
    if CURRENT_LAST_EVENT_TYPE >= pygame.NUMEVENTS:
        raise ValueError("Too many event types")
    return CURRENT_LAST_EVENT_TYPE


@public
def postNewEvent(*args, **kwargs):
    event = pygame.event.Event(*args, **kwargs)
    pygame.event.post(event)

public(
CHANGELEVEL = new_event_type(),
CHANGEPLAYLEVEL = new_event_type(),
SETOVERLAY = new_event_type()
)