from math import sin, pi
from random import random, randint
from lib.cell import add as add_vector
from lib.sprite import Sprite
from lib.filters import replace_color
from easing.circ import ease_out

from vfx import Vfx
import assets
from anims import Anim
from anims.flicker import FlickerAnim
from anims.offsetmove import OffsetMoveAnim
from colors.palette import WHITE, BLACK
from config import TILE_SIZE


class CloudPuffVfx(Vfx):
    class FloatAnim(Anim): pass

    def __init__(puff, src, dest, size, colors, *args, elev=0, **kwargs):
        super().__init__(kind=None, pos=(0, 0), *args, **kwargs)
        puff.dest = dest
        puff.size = size
        puff.elev = elev
        puff.colors = colors
        puff.anims = [
            *([OffsetMoveAnim(src, dest, speed=(2 + random()) * TILE_SIZE, easing=ease_out)]
                if src != dest
                else []),
            CloudPuffVfx.FloatAnim()
        ]
        puff.flickering = size != "large" and randint(1, 3) == 1
        puff.offset = tuple([(random() - 0.5) * 16 // 2 * 2 for i in range(2)])
        puff.offset_period = random() * 5
        puff.offset_amplitude = random() * 7
        puff.offset_direction = randint(0, 1) * 2 - 1
        puff.offset_axis = randint(0, 1)
        puff.update()

    def dissolve(puff, *args, duration=30, **kwargs):
        puff.anims.append(FlickerAnim(duration=duration, *args, **kwargs))

    def update(puff, *_):
        for anim in puff.anims:
            if anim.done:
                puff.anims.remove(anim)
                if isinstance(anim, FlickerAnim):
                    puff.anims.clear()
            else:
                puff.update_anim(anim)

        if not puff.anims:
            puff.done = True

    def update_anim(puff, anim):
        anim.update()

        if isinstance(anim, CloudPuffVfx.FloatAnim):
            if next((a for a in puff.anims if isinstance(a, OffsetMoveAnim)), None):
                x, y = puff.pos
            else:
                x, y = add_vector(puff.dest, puff.offset)
            PERIOD_X = 240 + puff.offset_period
            PERIOD_Y = 210 + puff.offset_period
            AMPLITUDE = 2 + puff.offset_amplitude
            xmod = anim.time // 3 * 3 % PERIOD_X / PERIOD_X
            ymod = anim.time // 3 * 3 % PERIOD_Y / PERIOD_Y
            if puff.offset_axis:
                xmod, ymod = ymod, xmod
            x += sin(xmod * puff.offset_direction * 2 * pi) * AMPLITUDE // 2 * 2
            y += sin(ymod * puff.offset_direction * 2 * pi) * AMPLITUDE // 2 * 2 - puff.elev * TILE_SIZE
            puff.pos = (x, y)
            return

        if isinstance(anim, OffsetMoveAnim):
            src_x, src_y = anim.src
            offset_x, offset_y = anim.offset
            puff.pos = add_vector(puff.offset, (
                src_x + offset_x,
                src_y + offset_y
            ))
            return

    def view(puff):
        flicker_anim = next((a for a in puff.anims if isinstance(a, FlickerAnim)), None)
        if (puff.done
        or flicker_anim and not flicker_anim.visible
        or not flicker_anim and puff.flickering and puff.anims and puff.anims[0].time // 2 % 2):
            return []

        color, color_alt = puff.colors
        if puff.size == "tiny":
            puff_image = assets.sprites["fx_particle"][0]
            if color_alt != BLACK:
                puff_image = replace_color(puff_image, BLACK, color_alt)
        elif puff.size == "small":
            puff_image = assets.sprites["fx_smallspark"]
            if color != BLACK:
                puff_image = replace_color(puff_image, BLACK, color)
        elif puff.size == "medium":
            puff_image = assets.sprites["fx_smoke_small"]
            if color_alt != WHITE:
                puff_image = replace_color(puff_image, WHITE, color_alt)
        elif puff.size == "large":
            puff_image = assets.sprites["fx_smoke_large"]
            if color != WHITE:
                puff_image = replace_color(puff_image, WHITE, color)

        puff_layer = "elems" if isinstance(puff.anim, OffsetMoveAnim) else "vfx"
        return [Sprite(
            image=puff_image,
            pos=add_vector(puff.pos, (TILE_SIZE // 4, TILE_SIZE // 4)),
            layer=puff_layer,
        )]
