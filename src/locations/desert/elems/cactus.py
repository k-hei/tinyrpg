from pygame.transform import flip
from lib.sprite import Sprite
import assets

from dungeon.actors import DungeonActor
from helpers.actor import Spritesheet
from cores import Core, Stats
from skills.weapon.tackle import Tackle

from random import random, choice
from lib.cell import is_adjacent
from anims.frame import FrameAnim

from anims.step import StepAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from config import PUSH_DURATION


class DesertEvilCactus(DungeonActor):
    spritesheet = Spritesheet(
        idle={
            (0, -1): assets.sprites["cactus_up"],
            (0, 1): assets.sprites["cactus_down"],
            (-1, 0): assets.sprites["cactus_side"],
            (1, 0): assets.sprites["cactus_side"],
        },
        move={
            (0, -1): (
                assets.sprites["cactus_up"],
                assets.sprites["cactus_move_up"],
                assets.sprites["cactus_move_up"],
                # flip(assets.sprites["cactus_move_up"], True, False),
                assets.sprites["cactus_up"],
            ),
            (0, 1): (
                assets.sprites["cactus_down"],
                assets.sprites["cactus_move_down"],
                assets.sprites["cactus_move_down"],
                # flip(assets.sprites["cactus_move_down"], True, False),
                assets.sprites["cactus_down"],
            ),
            (-1, 0): (
                assets.sprites["cactus_side"],
                assets.sprites["cactus_move_side"],
                assets.sprites["cactus_move_side"],
                assets.sprites["cactus_side"],
            ),
            (1, 0): (
                assets.sprites["cactus_side"],
                assets.sprites["cactus_move_side"],
                assets.sprites["cactus_move_side"],
                assets.sprites["cactus_side"],
            ),
        },
        attack={
            (0, -1): assets.sprites["cactus_attack_up"],
            (0, 1): assets.sprites["cactus_attack_down"],
            (-1, 0): assets.sprites["cactus_attack_side"],
            (1, 0): assets.sprites["cactus_attack_side"],
        },
        charge=assets.sprites["cactus_puff"],
        flinch=assets.sprites["cactus_flinch"],
    )

    idle_messages = [
        "The {enemy} hums a tune.",
        "The {enemy} cackles creepily.",
        "The {enemy} makes a pun.",
    ]

    def __init__(cactus, name="Cactriel", *args, **kwargs):
        super().__init__(Core(
            name=name,
            faction="enemy",
            stats=Stats(
                hp=40,
                st=12,
                dx=4,
                ag=5,
                en=8,
            ),
            skills=[Tackle],
        ), *args, **kwargs)

    def step(cactus, game):
        if not cactus.can_step():
            return None

        if not cactus.aggro:
            return super().step(game)

        enemy = game.find_closest_enemy(cactus)
        if not enemy:
            return None

        if random() < 1 / 16 and cactus.idle(game):
            game.anims.append([FrameAnim(
                target=cactus,
                frames=cactus.spritesheet.get_charge_sprites() * 5,
                frames_duration=5,
            )])
            return None

        return (("attack", enemy)
            if is_adjacent(cactus.cell, enemy.cell)
            else ("move_to", enemy.cell))

    def find_image(cactus, anims):
        if cactus.ailment == "freeze":
            return cactus.spritesheet.get_flinch_sprite()

        anim_group = [a for a in anims[0] if a.target is cactus] if anims else []
        for anim in anim_group:
            if isinstance(anim, StepAnim) and anim.duration == PUSH_DURATION:
                return cactus.spritesheet.get_attack_sprite(cactus.facing)[0]

            if isinstance(anim, StepAnim):
                walk_cycle = cactus.spritesheet.get_move_sprite(cactus.facing)
                walk_framecount = len(walk_cycle)
                walk_index = (anim.time - 1) // (anim.period // walk_framecount)
                return walk_cycle[walk_index % walk_framecount]

            if isinstance(anim, AttackAnim):
                attack_sprites = cactus.spritesheet.get_attack_sprite(cactus.facing)
                if anim.time >= 0:
                    return attack_sprites[int(anim.time >= anim.duration // 3)]

            if isinstance(anim, (FlinchAnim, FlickerAnim)):
                return cactus.spritesheet.get_flinch_sprite()

        return cactus.spritesheet.get_idle_sprite(cactus.facing)


    def view(cactus, anims):
        return super().view([Sprite(image=cactus.find_image(anims))], anims)
