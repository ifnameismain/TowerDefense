import pygame as pg


def create_text_object(text, font, position: tuple, color, max_size=(0, 0), line_width=20):
    words = [line.split(' ') for line in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = max_size
    x, y = position
    init_y = y
    text_obj = []
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if max_height != 0:
                if x + word_width >= max_width:
                    x = position[0]  # Reset the x.
                    y += word_height  # Start on new row.
            text_obj.append((word_surface, (x, y)))
            x += word_width + space
        x = position[0]  # Reset the x.
        y += word_height + line_width  # Start on new row.
        if max_height != 0:
            if y-init_y > max_height - 0.5*font.size(' ')[0]:
                break
    return text_obj


def centred_text(text, font, centre_pos: tuple, color):
    text_surface = font.render(text, 0, color)
    text_width, text_height = text_surface.get_size()
    return text_surface, (centre_pos[0]-0.5*text_width, centre_pos[1]-0.5*text_height)


def blit_text_object(surface, text_obj):
    if type(text_obj) == list:
        for word in text_obj:
            surface.blit(word[0], word[1])
    else:
        surface.blit(text_obj[0], text_obj[1])


def create_button(pos, size, color=pg.color.Color('white'),
                  text_color=pg.color.Color('black'), text=None, font=None):
    _rect = (pg.rect.Rect(pos[0], pos[1], size[0], size[1]), color)
    if text:
        text_obj = centred_text(text, font, (pos[0]+0.5*size[0],pos[1]+0.5*size[1]), text_color)
        return _rect, text_obj
    else:
        return _rect
