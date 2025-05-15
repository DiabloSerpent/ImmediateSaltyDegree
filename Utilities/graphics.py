import pygame, os, toml, math

class LoadedImage:
    def __init__(self, img, replace_color):
        self.surf = img
        self.main_colorkey = replace_color

    def fill_main(self, surf, color):
        if self.main_colorkey is None:
            return
        fill_color(surf, self.main_colorkey, color)

public(
images = {}
)
image_data = toml.load("./ImageData.toml")
for img in os.listdir("./Images"):
    bare_name = img[:img.index(".")]
    loaded = pygame.image.load("./Images/"+img)

    data = image_data[bare_name]
    scale = data.get("scale", 1)
    newSize = (loaded.get_width()*scale, loaded.get_height()*scale)
    loaded = pygame.transform.scale(loaded, newSize)
    colorkey = data.get("colorkey", (0, 0, 0))
    loaded.set_colorkey(colorkey)
    replace_color = data.get("replace_color", None)

    img_obj = LoadedImage(loaded, replace_color)
    images[bare_name] = img_obj


# Surprised this isn't already a method.
@public
def fill_color(surf, old_color, new_color):
    temp_surf = surf.copy()
    temp_surf.set_colorkey(old_color)
    surf.fill(new_color)
    surf.blit(temp_surf, (0, 0))

@public
def draw_line_from_center(surf, color, angle, width=2):
    rect = surf.get_rect()
    length = max(rect.size)
    s = rect.center
    e = [0, 0]
    e[0] = math.cos(angle) * length + s[0]
    e[1] = math.sin(angle) * length + s[1]
    pygame.draw.line(surf, color, s, e, width)
