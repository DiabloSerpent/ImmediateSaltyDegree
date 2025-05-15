import pygame
from pygame.sprite import Sprite, Group

"""def publicizer(module_all):
    def _publicize(thing, name=None):
        if not name:
            module_all.append(thing.__name__)
        else:
            module_all.append(name)"""

#Unfinished
@public
class LevelSprites(Group):
    Inputs = {}
    Inputs["updateMPos"] = pygame.mouse.get_pos
    Inputs["updateMPressed"] = pygame.mouse.get_pressed
    Inputs["updateKeys"] = pygame.key.get_pressed

    def update(self):
        # Different LevelSprite instances might
        # have different inputs, but oh well. Setting
        # a class variable to the inputs slows
        # things way down for some reason.
        inputs = {k: v() for k, v in self.Inputs.items()}
        for spr in self.sprites():
            # This might be slow, idk
            for name, input_state in inputs.items():
                updater = getattr(spr, name, False)
                if updater:
                    updater(input_state)

            spr.update()

    # Doesn't do all the things Group.draw does,
    # but I wasn't planning on using those
    # features anyway.
    def draw(self, screen: pygame.Surface):
        for spr in self.sprites():
            if hasattr(spr, "draw"):
                spr.draw(screen)
            else:
                screen.blit(spr.image, spr.rect)

    # Method for getting all sprites of a certain type
    def get(self, Type=Sprite):
        for spr in self.sprites():
            if isinstance(spr, Type):
                # Use generators cuz they're cool
                yield spr

    # Does the same thing as get, but returns
    # as a list.
    def getList(self, Type=Sprite):
        return list(self.get(Type))


# 200 iq move here
@public
class AttrCollector:
    pass


@public
class KeyCombo:
    def __init__(self, *combo):
        self.pattern = []
        self.state = []
        for key, frames in zip(combo[::2], combo[1::2]):
            self.pattern.append({
                "ID": abs(key),
                "state": int(key > 0),
                "min": frames[0],
                "max": frames[1]
            })
            self.state.append({
                "count": 0,
                "matched": False
            })
        self.stage = 0
        self.hasMatch = False

    def __repr__(self):
        # Debugging info
        zipped_info = zip(self.pattern, self.state)
        info = []
        for pair in zipped_info:
            info.extend(pair)
        return "\n".join(map(str, info))

    def update(self, keys):
        # When current stage condition isn't met,
        # move on to next stage.
        # Once the last stage's condition isn't
        # met, clear the match.
        #
        # If the stage's condition has been met, update
        # the count for the stage.
        #
        # Then, evaluate the match
        current = self.pattern[self.stage]
        state = self.state[self.stage]
        if keys[current["ID"]] == current["state"]:
            state["count"] += 1
        else:
            if self.stage+1 < len(self.pattern):
                self.stage += 1

                # Makes sure that the first frame of the
                # next stage is actually counted.
                next_p = self.pattern[self.stage]
                next_state = self.state[self.stage]
                if keys[next_p["ID"]] == next_p["state"]:
                    next_state["count"] += 1
            else:
                self.clearMatch()
        self.evaluateMatch()
        if self.stage > 0:
            if not self.state[self.stage-1]["matched"]:
                self.clearMatch()

    def evaluateMatch(self):
        # For each stage in the match, check if the
        # count is between that stage's min and max.
        # For the max, None is interpreted as infinity.
        # If any count is outside that range,
        # there is no match.
        self.hasMatch = True
        for stage, state in zip(self.pattern, self.state):
            if state["count"] <= stage["min"]:
                self.hasMatch = False
                state["matched"] = False
            elif stage["max"] is None:
                state["matched"] = True
            elif state["count"] >= stage["max"]:
                self.hasMatch = False
                state["matched"] = False
            else:
                state["matched"] = True

    def clearMatch(self):
        # For each stage in the match, set the count to 0
        for stage in self.state:
            stage["count"] = 0
        self.stage = 0


# I haven't decided if this should be used yet.
@private
class HasColorDict:
    def __init__(self, *args, **kwargs):
        self.colors = {}
    def __getattr__(self, name):
        if name in self.colors:
            return self.colors[name]
        return super().__getattr__(name)