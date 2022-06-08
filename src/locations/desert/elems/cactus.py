from random import random
from pygame.transform import flip
from lib.sprite import Sprite
import assets

from dungeon.actors import DungeonActor
from helpers.actor import Spritesheet
from cores import Core, Stats
from skills.weapon.tackle import Tackle

from lib.cell import is_adjacent, neighborhood
from anims.frame import FrameAnim

from anims.step import StepAnim
from anims.shake import ShakeAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.bounce import BounceAnim
from config import PUSH_DURATION

from skills.attack import AttackSkill
from vfx.cactus_spine import CactusSpineVfx


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

    class ChargeAnim(ShakeAnim): pass

    class Blowout(AttackSkill):
        name = "Blowout"
        charge_turns = 1

        def effect(game, user, dest=None, on_start=None, on_end=None):

            def blowout():
                directions = neighborhood((0, 0), diagonals=True)
                for direction in directions:
                    game.vfx.append(CactusSpineVfx(
                        src=user.cell,
                        color=user.color(),
                        direction=direction,
                    ))

                target_cells = neighborhood(user.cell, diagonals=True)
                target_actors = [e for e in game.stage.elems
                    if isinstance(e, DungeonActor) and e.cell in target_cells]

                for target in target_actors:
                    game.attack(
                        actor=user,
                        target=target,
                        atk_mod=0.95,
                        crit_mod=50,
                        animate=False,
                    )

            game.anims.append([BounceAnim(
                target=user,
                duration=30,
                on_start=on_start,
                on_squash=blowout,
                on_end=on_end,
            )])

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
            message=[
                (name, "...And now they're making GhostBusters with only women!"),
                (name, "What's going on??")
            ],
        ), *args, **kwargs)
        cactus.damaged = False

    def damage(cactus, *args, **kwargs):
        super().damage(*args, **kwargs)
        cactus.damaged = True

    def step(cactus, game):
        if not cactus.can_step():
            return None

        if not cactus.aggro:
            return super().step(game)

        enemy = game.find_closest_enemy(cactus)
        if not enemy:
            return None

        if random() < 1 / 16 and cactus.idle(game):
            game.anims[-1].append(FrameAnim(
                target=cactus,
                frames=cactus.spritesheet.get_charge_sprites() * 5,
                frames_duration=5,
            ))
            return None

        if not is_adjacent(cactus.cell, enemy.cell):
            return ("move_to", enemy.cell)

        blowout_chance = 7 / 8 if cactus.damaged else 1 / 2
        cactus.damaged = False

        if random() < blowout_chance:
            return cactus.charge(skill=DesertEvilCactus.Blowout, dest=enemy.cell)
        else:
            return ("attack", enemy)

    def find_image(cactus, anims):
        if cactus.ailment == "freeze":
            return cactus.spritesheet.get_flinch_sprite()

        anim_group = [a for a in anims[0] if a.target is cactus] if anims else []
        anim_group += cactus.core.anims

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

            if isinstance(anim, ShakeAnim):
                charge_sprites = cactus.spritesheet.get_charge_sprites()
                charge_index = anim.time // 5 % len(charge_sprites)
                return charge_sprites[charge_index]

            if isinstance(anim, BounceAnim):
                charge_sprites = cactus.spritesheet.get_charge_sprites()
                return charge_sprites[int(anim.phase == "squash")]

        return cactus.spritesheet.get_idle_sprite(cactus.facing)

    def view(cactus, anims):
        return super().view([Sprite(image=cactus.find_image(anims))], anims)
