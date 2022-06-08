from lib.sprite import Sprite
import assets
from cores import Core
from cores.biped import SpriteMap
from anims.walk import WalkAnim
from config import BUNNY_NAME


class Bunny(Core):
    name = BUNNY_NAME
    sprites = SpriteMap(
        face_right=assets.sprites["bunny"],
        face_down=assets.sprites["bunny_down"],
        face_up=assets.sprites["bunny_up"],
        walk_right=assets.sprites["bunny_walk"],
        walk_down=assets.sprites["bunny_walk_down"],
        walk_up=assets.sprites["bunny_walk_up"],
    )

    class WalkAnim(WalkAnim):
        period = 12
        frame_count = 3

    def __init__(bunny, faction="enemy", *args, **kwargs):
        super().__init__(
            name=Bunny.name,
            faction=faction,
            *args, **kwargs)

    def view(bunny):
        surface = None
        facing_x, facing_y = bunny.facing
        flip_x, flip_y = facing_x == -1, False

        for anim in bunny.anims:
            if isinstance(anim, bunny.WalkAnim):
                if facing_x == -1 or facing_x == 1:
                    walk_cycle = bunny.sprites.walk_right
                elif facing_y == -1:
                    walk_cycle = bunny.sprites.walk_up
                elif facing_y == 1:
                    walk_cycle = bunny.sprites.walk_down
                surface = walk_cycle[anim.frame_index]
                break
        else:
            if facing_x == 1 or facing_x == -1:
                surface = bunny.sprites.face_right
            elif facing_y == 1:
                surface = bunny.sprites.face_down or bunny.sprites.face_right
            elif facing_y == -1:
                surface = bunny.sprites.face_up or bunny.sprites.face_right

        sprite = Sprite(
            image=surface,
            flip=(flip_x, flip_y),
            layer="elems"
        ) if surface else None
        sprites = [sprite] if sprite else []
        return super().view(sprites)
