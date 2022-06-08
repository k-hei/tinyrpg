from pygame.transform import flip, rotate
import lib.vector as vector
from lib.filters import replace_color
from lib.sprite import Sprite
import assets

from vfx import Vfx
from anims import Anim
from colors.palette import BLACK, RED
from config import TILE_SIZE


class CactusSpineVfx(Vfx):
    speed = 3
    duration = 15

    def __init__(fx, src, direction, *args, color=RED, on_end=None, **kwargs):
        normal = vector.normalize(direction)
        super().__init__(
            kind=None,
            pos=vector.add(
                vector.scale(normal, TILE_SIZE / 8),
                [(x + 0.5) * TILE_SIZE for x in src]
            ),
            *args,
            **kwargs
        )
        fx.src = src
        fx.direction = direction
        fx.velocity = vector.scale(normal, fx.speed)
        fx.color = color
        fx.on_end = on_end
        fx.anim = Anim(duration=fx.duration)
        fx.image = {
            (0, -1): assets.sprites["cactus_spine"],
            (1, -1): assets.sprites["cactus_spine_diag"],
            (1, 0): rotate(assets.sprites["cactus_spine"], 270),
            (1, 1): flip(assets.sprites["cactus_spine_diag"], False, True),
            (0, 1): flip(assets.sprites["cactus_spine"], False, True),
            (-1, 1): flip(assets.sprites["cactus_spine_diag"], True, True),
            (-1, 0): rotate(assets.sprites["cactus_spine"], 90),
            (-1, -1): flip(assets.sprites["cactus_spine_diag"], True, False),
        }[direction]

    def update(fx, *_):
        if not fx.anim:
            return

        if fx.anim.done:
            fx.anim = None
            fx.done = True
            if fx.on_end:
                fx.on_end()
            return

        fx.pos = vector.add(fx.pos, fx.velocity)
        fx.anim.update()

    def view(fx):
        if fx.done or fx.anim and fx.anim.time % 2:
            return []

        fx_image = fx.image
        if fx.color != BLACK:
            fx_image = replace_color(fx_image, BLACK, fx.color)

        return [Sprite(
            image=fx_image,
            pos=fx.pos,
            origin=Sprite.ORIGIN_CENTER,
            layer="vfx",
        )]
