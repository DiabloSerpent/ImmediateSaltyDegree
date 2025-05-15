import pygame
from ..math import *

# I would love to subclass this to Rect,
# but I have no clue how all of the internal
# variables work in it

# ^> I read through some of the pygame library and
# found out that Rect is written in C, which might
# make that a bit difficult.
# However, the Rect class only has x, y, h, and w
# as actual attributes, and the rest are calculated as
# needed.

# ^> Dunno what I was thinking. Subclassing was very easy.

# Used for circular objects/provides geometry functions
@public
class Circle(pygame.Rect):
    def __init__(self, center, radius):
        super().__init__(center[0] - radius, center[1] - radius, radius*2, radius*2)

    def __eq__(self, value):
        if type(value) is Circle:
            return self.topleft == value.topleft and self.w == value.w
        return False

    '''def __getattr__(self, attr):
        # This should really be a subclass to Rect
        return getattr(self._rect, attr)'''

    def get_rect(self):
        return pygame.Rect(self)

    '''# Create center as property instead of variable
    # to avoid having to set it everytime self.x or
    # self.y is changed.
    @property
    def center(self):
        return self.x, self.y

    @center.setter
    def center(self, newcenter):
        self.x = newcenter[0]
        self.y = newcenter[1]'''

    # h and w should always be equal
    @property
    def h(self):
        return self.w

    @h.setter
    def h(self, value):
        self.w = value

    @property
    def height(self):
        return self.w

    @height.setter
    def height(self, value):
        self.w = value

    @property
    def size(self):
        return self.w, self.w

    @size.setter
    def size(self, value):
        self.w = value[0]

    @property
    def d(self):
        return self.w

    @d.setter
    def d(self, newD):
        self.w = newD

    @property
    def r(self):
        # r should be an integer
        return self.w // 2

    @r.setter
    def r(self, newR):
        self.w = newR * 2

    '''# returns a moved version of self
    def move(self, dx, dy):
        newCenter = (dx, dy)  # Convenience
        newCenter = [self.center[x] - newCenter[x] for x in (0, 1)]
        return Circle(newCenter, self.r)

    # Moves circle
    def move_ip(self, dx, dy):
        self._rect.move_ip(dx, dy)

    # Resizes circle
    def inflate_ip(self, dr):
        self.r *= dr
        self._rect = pygame.Rect(self.x-self.r, self.y-self.r, self.d, self.d)'''

    # Tests if a point is in the circle
    def collidepoint(self, p):
        rhyp = pointdist_sq(self.center, p)
        # Avoid using sqrt in favor of ^2
        return self.r ** 2 >= rhyp

    # Test if Circle intersects Rect
    def colliderect(self, rect):
        #  Avoid unnecessary math, might be overkill though
        # if self._rect doesn't collide with rect,
        # neither does the circle
        if not super().colliderect(rect):
            return False
        # Find closest point on rect to circle
        closestp = clamp_to_rect(rect, self.center)
        # If closestp is in the circle, it collides
        return self.collidepoint(closestp)

    def collidecirc(self, circ):
        rhyp = pointdist_sq(self.center, circ.center)
        # Avoid using sqrt in favor of ^2
        return (self.r ** 2 + circ.r ** 2) >= rhyp
