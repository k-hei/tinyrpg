from math import cos, sin, pi
from random import random, randint, randrange, choice
from dungeon.props import Prop
from assets import load as use_assets
from anims.frame import FrameAnim
from anims.pause import PauseAnim
from filters import replace_color, recolor
from comps.skill import Skill
from contexts.dialogue import DialogueContext
from vfx import Vfx
from palette import BLACK
from sprite import Sprite
import config

class Soul(Prop):
  ANIM_FRAMES = 5
  ANIM_PERIOD = 45
  ANIM_SWIVEL_PERIOD = 120
  ANIM_SWIVEL_AMP = 5
  ANIM_FLOAT_PERIOD = 75
  ANIM_FLOAT_AMP = 4
  BOUNCE_AMP = 5
  ACCEL = 0.25
  FRAMES = ["fx_soul0", "fx_soul1", "fx_soul2", "fx_soul3", "fx_soul4"]

  def __init__(soul, skill=None):
    super().__init__(solid=False)
    soul.skill = skill
    soul.obtaining = False
    soul.anim = FrameAnim(frames=Soul.FRAMES, duration=45, loop=True)
    soul.pos = (0, 0)
    soul.norm = (0, 0)
    soul.vel = 0
    soul.vpos = 0
    soul.vfx = []
    soul.on_end = None

  def obtain(soul, game):
    game.floor.elems.remove(soul)
    game.learn_skill(soul.skill)
    game.open(DialogueContext(
      lite=True,
      script=[
        (None, ("Obtained skill ", soul.skill().token(), "!")),
        "Equip it with the CUSTOM menu (press 'B')."
      ]
    ))

  def burst(soul, game):
    col, row = soul.cell
    x = col * config.TILE_SIZE
    y = row * config.TILE_SIZE
    game.vfx.append(Vfx(
      kind="burst",
      pos=(x, y),
      color=soul.skill.color,
      anim=FrameAnim(
        duration=15,
        frames=["fx_burst0", "fx_burst1", "fx_burst2", "fx_burst3", "fx_burst4"]
      )
    ))
    r = 0
    while r < 2 * pi:
      r += pi / 4 * random()
      norm_x = cos(r)
      norm_y = sin(r)
      start_x = x + norm_x * 16
      start_y = y + norm_y * 16
      vel_x = norm_x * random() * 2
      vel_y = norm_y * random() * 2
      kind = choice(("spark", "smallspark"))
      game.vfx.append(Vfx(
        kind=kind,
        pos=(start_x, start_y),
        vel=(vel_x, vel_y),
        color=soul.skill.color,
        anim=FrameAnim(
          duration=randint(15, 45),
          frames=[
            "fx_{}0".format(kind),
            "fx_{}1".format(kind),
            "fx_{}2".format(kind)
          ]
        )
      ))

  def effect(soul, game):
    r = 2 * pi * random()
    soul.norm = (cos(r), sin(r))
    soul.vel = Soul.BOUNCE_AMP
    soul.obtaining = True
    soul.on_end = lambda: (
      soul.burst(game),
      soul.obtain(game)
    )
    game.anims.append([ PauseAnim(duration=180) ])
    if game.log.active:
      game.log.exit()

  def update(soul):
    soul.anim.update()
    pos_x, pos_y = soul.pos
    if soul.obtaining:
      norm_x, norm_y = soul.norm
      pos_x += norm_x * soul.vel
      pos_y += norm_y * soul.vel
      soul.vpos += soul.vel
      soul.vel -= Soul.ACCEL
      if soul.vpos <= 0 and soul.on_end:
        soul.on_end()
    else:
      tx = soul.anim.time % Soul.ANIM_SWIVEL_PERIOD / Soul.ANIM_SWIVEL_PERIOD
      ty = soul.anim.time % Soul.ANIM_FLOAT_PERIOD / Soul.ANIM_FLOAT_PERIOD
      pos_x = cos(pi * 2 * tx) * Soul.ANIM_SWIVEL_AMP
      pos_y = sin(pi * 2 * ty) * Soul.ANIM_FLOAT_AMP
      if soul.anim.time % randint(30, 45) == 0:
        col, row = soul.cell
        x = (col + 0.5) * config.TILE_SIZE + pos_x + random()
        y = (row + 0.5) * config.TILE_SIZE + pos_y + random() + 8
        kind = choice(("spark", "smallspark"))
        soul.vfx.append(Vfx(
          kind=kind,
          pos=(x, y),
          vel=(0, 0.25),
          color=soul.skill.color,
          anim=FrameAnim(
            duration=60,
            frames=[
              "fx_{}0".format(kind),
              "fx_{}1".format(kind),
              "fx_{}2".format(kind)
            ]
          )
        ))
    soul.pos = (pos_x, pos_y)

  def view(soul, anims):
    sprites = []
    assets = use_assets()
    soul_color = soul.skill.color
    soul_image = assets.sprites[soul.anim.frame]
    soul_image = replace_color(soul_image, BLACK, soul_color)
    sprites.append(Sprite(
      image=soul_image,
      pos=soul.pos,
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
        layer="elems"
      ))
    return super().view(sprites, anims)
