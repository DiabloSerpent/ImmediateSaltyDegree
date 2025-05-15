import pygame, math

# Restricts var to be between lowest and highest
@public
def clamp(var, lowest, highest):
    if var < lowest:
        return lowest
    if var > highest:
        return highest
    else:
        return var


@public
def clamp_to_rect(rect, p):
    p = list(p)
    # The bottom/right edges of the rect aren't
    # actually on the rect.
    p[0] = clamp(p[0], rect.left, rect.right-1)
    p[1] = clamp(p[1], rect.top, rect.bottom-1)
    return tuple(p)


# Returns inNo flattened to flatvalue
@public
def flatten(inNo, flatvalue):
    if inNo == 0:
        return 0
    if inNo < 0:
        flatvalue *= -1
    return flatvalue

#  This should be removed

# Returns a reference to the corner of a Rect that
# is closest to the offset from the center of the
# rect by (x, y)
@public
def getCorner(rect, x, y):
    # McCabe, I hope you're happy
    if y >= 0:
        corner = "bottom"
    else:
        corner = "top"
    if x >= 0:
        corner += "right"
    else:
        corner += "left"
    return getattr(rect, corner)


#  This function is being used to test
#  different documentation techniques.
@public
def two_points_to_rect(tl, br) -> pygame.Rect:
    # I now love these, they are going everywhere
    # (eventually)
    """Creates a Rect from 2 points:
    - __tl__ is the top left corner
    - __br__ is the bottom right corner
    """

    rect = pygame.Rect(
        tl[0],
        tl[1],
        br[0]-tl[0],
        br[1]-tl[1])
    rect.normalize()
    return rect


# Basically math.atan2, but nicer on me
@public
def atan2(deltx, delty) -> float:
    angle = math.atan2(delty, deltx)
    '''angle = 0
    # Avoid dividing by zero
    if deltx == 0:
        if delty >= 0:
            angle = math.radians(270)
        else:
            angle = math.radians(90)
    else:
        # Use arctangent to determine angle
        angle = math.atan(-delty/deltx)
        # However, atan doesn't deliver a clean number,
        # which the below is used to combat
        if delty > 0:
            if angle > 0:
                angle += math.pi
            else:
                angle += math.pi * 2
        if deltx < 0:
            if delty == 0:
                angle = math.pi
            elif delty < 0:
                angle += math.pi'''
    if angle < 0:
        angle += math.pi * 2
    return angle


# Pythagorean theorem squared
@public
def hyp_sq(leg1, leg2):
    leg1 **= 2
    leg2 **= 2
    return leg1 + leg2


# Pythagorean theorem exact
@public
def hyp_ex(leg1, leg2):
    return hyp_sq(leg1, leg2)**0.5


# Returns distance from p1 to p2 squared
@public
def pointdist_sq(p1, p2):
    rpos = (p2[0] - p1[0], p2[1] - p1[1])
    return hyp_sq(*rpos)


# Returns exact distance from p1 to p2
@public
def pointdist_ex(p1, p2):
    return pointdist_sq(p1, p2)**0.5


@public
def rotate_around_to(center, point, angle, *, deg=False):
    if deg:
        angle = math.radians(angle)
    rotated = [point[x] - center[x] for x in (0, 1)]
    dist = hyp_ex(*rotated)
    rotated = (math.cos(angle) * dist, math.sin(angle) * dist)
    return tuple(rotated[x] + center[x] for x in (0, 1))


@public
def rotate_around_by(center, point, angle, *, deg=False):
    if deg:
        angle = math.radians(angle)
    rotated = [point[x] - center[x] for x in (0, 1)]
    # This line seperates this function from the above
    angle += atan2(*rotated)
    dist = hyp_ex(*rotated)
    rotated = (math.cos(angle) * dist, math.sin(angle) * dist)
    return tuple(rotated[x] + center[x] for x in (0, 1))
