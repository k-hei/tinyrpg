from math import cos, sin, pi, sqrt
from random import random, randint, randrange, choice
from lib.cell import add as add_vector, subtract as subtract_vector
import lib.vector as vector
from dungeon.props import Prop
from assets import load as use_assets
from anims.frame import FrameAnim
from anims.pause import PauseAnim
from lib.filters import replace_color, recolor
from comps.skill import Skill
from contexts.dialogue import DialogueContext
from vfx import Vfx
from vfx.burst import BurstVfx
from vfx.particle import ParticleVfx
from colors.palette import BLACK, WHITE
from lib.sprite import Sprite
from config import TILE_SIZE

class Soul(Prop):
  ANIM_FRAMES = 5
  ANIM_PERIOD = 45
  ANIM_SWIVEL_PERIOD = 120
  ANIM_SWIVEL_AMP = 5
  ANIM_FLOAT_PERIOD = 75
  ANIM_FLOAT_AMP = 4
  BOUNCE_AMP = 5
  ACCEL = 0.25

  class PulsateAnim(FrameAnim):
    frames = ["fx_soul0", "fx_soul1", "fx_soul2", "fx_soul3", "fx_soul4"]
    frames_duration = 9
    loop = True

  active = True

  def __init__(soul, contents=None):
    super().__init__(solid=False)
    soul.skill = contents
    soul.obtain_target = False
    soul.anim = Soul.PulsateAnim(delay=randint(0, 120))
    soul.offset = (0, 0)
    soul.norm = (0, 0)
    soul.vel = 0
    soul.vfx = []
    soul.on_end = None

  def obtain(soul, game):
    game.stage.elems.remove(soul)
    game.store.learn_skill(soul.skill)
    game.open(DialogueContext(
      lite=True,
      script=[
        (None, ("Obtained skill ", soul.skill().token(), "!")),
        "Equip it with the EQUIP menu (press START)."
      ]
    ))

  def burst(soul, game):
    target_cell = add_vector(soul.cell, tuple([x // TILE_SIZE for x in soul.obtain_target]))
    x, y = tuple([x * TILE_SIZE for x in target_cell])
    game.vfx.append(BurstVfx(
      cell=target_cell,
      color=soul.skill.color,
    ))

  # TODO: more vector helpers
  def effect(soul, game, actor):
    if actor != game.hero:
      return False
    target_x, target_y = tuple([x * TILE_SIZE for x in subtract_vector(actor.cell, soul.cell)])
    pos_x, pos_y = soul.offset
    dist_x = target_x - pos_x
    dist_y = target_y - pos_y
    dist = sqrt(dist_x * dist_x + dist_y * dist_y) or 1
    soul.norm = (-dist_x / dist, -dist_y / dist)
    soul.vel = Soul.BOUNCE_AMP
    soul.obtain_target = (target_x, target_y)
    soul.on_end = lambda: (
      soul.burst(game),
      soul.obtain(game)
    )
    game.anims.append([ PauseAnim(duration=60) ])
    return True

  def update(soul, game):
    soul.anim.update()
    pos_x, pos_y = soul.offset
    particles = []
    if soul.obtain_target:
      target_x, target_y = soul.obtain_target
      dist_x = target_x - pos_x
      dist_y = target_y - pos_y
      norm_x, norm_y = soul.norm
      pos_x += norm_x * soul.vel
      pos_y += norm_y * soul.vel
      postdist_x = target_x - pos_x
      postdist_y = target_y - pos_y
      if soul.vel and (
        dist_x / abs(dist_x or 1) != postdist_x / abs(postdist_x or 1)
        or dist_y / abs(dist_y or 1) != postdist_y / abs(postdist_y or 1)
      ):
        soul.on_end and soul.on_end()
      soul.vel -= Soul.ACCEL
      if soul.vel == 0:
        dist = sqrt(dist_x * dist_x + dist_y * dist_y) or 1
        soul.norm = (-dist_x / dist, -dist_y / dist)
    else:
      tx = soul.anim.time % Soul.ANIM_SWIVEL_PERIOD / Soul.ANIM_SWIVEL_PERIOD
      ty = soul.anim.time % Soul.ANIM_FLOAT_PERIOD / Soul.ANIM_FLOAT_PERIOD
      pos_x = cos(pi * 2 * tx) * Soul.ANIM_SWIVEL_AMP
      pos_y = sin(pi * 2 * ty) * Soul.ANIM_FLOAT_AMP
      if soul.anim.time % randint(30, 45) < 5 and soul.cell in (game.hero.visible_cells if game.hero else []):
        particles.append(ParticleVfx(
          pos=vector.add(soul.rect.center, soul.offset),
          color=choice([soul.skill.color, WHITE]),
        ))
    soul.offset = (pos_x, pos_y)
    return particles

  def view(soul, anims):
    sprites = []
    assets = use_assets()
    soul_color = soul.skill.color
    soul_image = assets.sprites[soul.anim.frame()]
    soul_image = replace_color(soul_image, BLACK, soul_color)
    sprites.append(Sprite(
      image=soul_image,
      pos=soul.offset,
      layer="vfx"
    ))
    for fx in soul.vfx:
      if fx.done:
        soul.vfx.remove(fx)
        continue
      fx_frame = fx.update()
      fx_image = assets.sprites[fx_frame]
      fx_image = recolor(fx_image, fx.color)
      sprites.append(Sprite(
        image=fx_image,
        pos=fx.pos,
        origin=("center", "center"),
        layer="elems",
        offset=16
      ))
    return super().view(sprites, anims)
