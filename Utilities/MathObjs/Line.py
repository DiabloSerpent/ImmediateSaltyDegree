from ..math import *

@public
class Line:
    def __init__(self, pone, ptwo):
        self.start = pone
        self.end = ptwo
        #self.updateEq()
        # Determines the bounds of the line
        # in the actual maths
        self.rect = two_points_to_rect(pone, ptwo)
        # The rect collide functions are sometimes
        # funky with 0-length sides
        if self.rect.width == 0:
            self.rect.move_ip(-1, 0)
            self.rect.width = 2
        if self.rect.height == 0:
            self.rect.move_ip(0, -1)
            self.rect.height = 2

    #  Neither a, b, or c should be assigned to.
    @property
    def a(self):
        return self.end[0] - self.start[0]

    @property
    def b(self):
        return self.start[1] - self.end[1]

    @property
    def c(self):
        return self.a * self.start[1] + self.b * self.start[0]

    # Made to avoid redundant calculations
    @property
    def slope(self):
        """True == + slope, False == - slope"""
        return (self.a >= 0) != (self.b >= 0)

    # Updates the line equation
    def updateEq(self):
        # Line is stored in standard form to avoid
        # dividing by zero.
        self.a = self.end[0] - self.start[0]
        self.b = self.start[1] - self.end[1]
        if self.a == 0 and self.b == 0:
            raise ValueError(f"{self} does not form a line")
        self.c = self.a * self.start[1] + self.b * self.start[0]
        # slope variable made to avoid redundant calculations
        # True == + slope, False == - slope
        self.slope = (self.a >= 0) != (self.b >= 0)

    def __str__(self):
        return f"Line {self.start}, {self.end}"

    def _checkBounds(self, bounds, shape):
        if bounds == "ignore":
            return True

        if type(shape) == tuple:
            collides = self.rect.collidepoint(shape)
        else:
            collides = shape.colliderect(self.rect)


        if bounds == "inside":
            return collides
        elif bounds == "outside":
            return not collides
        else:
            return None

    def getX(self, yVal):
        return (-self.a * yVal + self.c) / self.b

    def getY(self, xVal):
        return (-self.b * xVal + self.c) / self.a

    def getIntersectionX(self, line):
        top = self.a * line.c - line.a * self.c
        bottom = line.b * self.a - self.b * line.b
        if bottom == 0:
            if top == 0:
                return self
            else:
                return None
        return top / bottom

    # Uses the line's slope to reflect a point across itself
    def reflectpoint(self, p):
        n = list(p)
        if self.a == 0:
            xDiff = self.start[0] - p[0]
            n[0] = self.start[0] + xDiff
            # n[1] remains unchanged
        elif self.b == 0:
            # n[0] remains unchanged
            yDiff = self.start[1] - p[1]
            n[1] = self.start[1] + yDiff
        else:
            n[0] = self.getX(p[1])
            n[1] = self.getY(p[0])
        return tuple(n)

    #  The main point of this function is to provide a
    #  distinction between both sides of the line,
    #  not necesarily meaning that returning True
    #  means the point is above the line.
    # Returns which side of the line a given point is on
    def side(self, point):
        # Finds reflected point
        rpoint = self.reflectpoint(point)
        if point[1] == rpoint[1]:
            # If the point is on the line
            if point[0] == rpoint[0]:
                return None
            # If the line is vertical
            else:
                return point[0] > rpoint[0]
        # If the line is not vertical
        else:
            return point[1] > rpoint[1]

    # Checks if a given point is on the line
    def collidepoint(self, p, bounds="inside"):
        if not self._checkBounds(bounds, p):
            return False
        # Quicker than using side(), maybe
        reflected = self.reflectpoint(p)
        return reflected == p

    # Checks if given Rect intersects with the line
    def colliderect(self, rect, bounds="inside"):
        if not self._checkBounds(bounds, rect):
            return False
        # Checks which corners are opposite to the line
        # If slope is positive,
        if self.slope:
            # use topright/bottomleft as corners checked
            c1 = self.side(rect.topright)
            c2 = self.side(rect.bottomleft)
        # If slope is negative,
        else:
            # use topleft/bottomright as corners checked
            c1 = self.side(rect.topleft)
            c2 = self.side(rect.bottomright)
        #  Checking corner 2 isn't required due to
        #  equality check at bottom
        # If the corner 1 is on the line, return true
        if c1 is None:
            return True
        # If corner 1 is on a different side to
        # corner 2, the rect is colliding
        return c1 != c2


    # Tests whether circ is on the wall
    def collidecirc(self, circ, bounds="inside"):
        if not self._checkBounds(bounds, circ):
            return False
        # Basically, check if circ collides with itself
        # reflected across the line
        reflectedP = self.reflectpoint(circ.center)
        distance = pointdist_ex(reflectedP, circ.center)
        return distance <= circ.r * 2

    #Unfinished
    def collideline(self, line, bounds="inside", otherbounds="inside"):
        intersectX = self.getIntersectionX(line)
        if intersectX is self:
            return True
        elif intersectX is None:
            return False

        if self.a != 0:
            intersectP = (intersectX, self.getY(intersectX))
        else:
            intersectP = (intersectX, self.start[1])

        if not self._checkBounds(bounds, intersectP):
            return False
        if not line._checkBounds(otherbounds, intersectP):
            return False
        else:
            return True
