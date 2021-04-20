from props import Prop
from assets import load as use_assets
from anims.frame import FrameAnim
from anims.pause import PauseAnim
from filters import replace_color
from comps.skill import Skill
from comps.vfx import Vfx
from skills import get_sort_order
import palette
import random
import math
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

  def __init__(soul, skill=None):
    super().__init__(solid=False)
    soul.skill = skill
    soul.time = random.randrange(0, Soul.ANIM_SWIVEL_PERIOD)
    soul.obtaining = False
    soul.pos = (0, 0)
    soul.norm = (0, 0)
    soul.vel = 0
    soul.vpos = 0
    soul.on_end = None

  def obtain(soul, game):
    if not soul.skill in game.skill_pool:
      game.new_skills.append(soul.skill)
      game.skill_pool.append(soul.skill)
      game.skill_pool.sort(key=get_sort_order)
    game.log.print("Obtained skill \"" + soul.skill.name + "\"!")
    game.log.print("Equip it with the CUSTOM menu (press 'B').")
    game.floor.elems.remove(soul)

  def burst(soul, game):
    col, row = soul.cell
    x = col * config.TILE_SIZE
    y = row * config.TILE_SIZE
    game.vfx.append(Vfx(
      kind="burst",
      pos=(x, y),
      color=Skill.get_color(soul.skill),
      anim=FrameAnim(
        duration=15,
        frame_count=5
      )
    ))
    r = 0
    while r < 2 * math.pi:
      r += math.pi / 4 * random.random()
      norm_x = math.cos(r)
      norm_y = math.sin(r)
      start_x = x + norm_x * 16
      start_y = y + norm_y * 16
      vel_x = norm_x * random.random() * 2
      vel_y = norm_y * random.random() * 2
      game.vfx.append(Vfx(
        kind="spark",
        pos=(start_x, start_y),
        vel=(vel_x, vel_y),
        color=Skill.get_color(soul.skill),
        anim=FrameAnim(
          duration=random.randint(15, 45),
          frame_count=3
        )
      ))

  def effect(soul, game):
    r = 2 * math.pi * random.random()
    soul.norm = (math.cos(r), math.sin(r))
    soul.vel = Soul.BOUNCE_AMP
    soul.obtaining = soul.time
    soul.on_end = lambda: (
      soul.burst(game),
      soul.obtain(game)
    )
    game.anims.append([ PauseAnim(duration=180) ])

  def update(soul, vfx):
    soul.time += 1
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
      tx = soul.time % Soul.ANIM_SWIVEL_PERIOD / Soul.ANIM_SWIVEL_PERIOD
      ty = soul.time % Soul.ANIM_FLOAT_PERIOD / Soul.ANIM_FLOAT_PERIOD
      pos_x = math.cos(math.pi * 2 * tx) * Soul.ANIM_SWIVEL_AMP
      pos_y = math.sin(math.pi * 2 * ty) * Soul.ANIM_FLOAT_AMP
      if soul.time % random.randint(30, 45) == 0:
        col, row = soul.cell
        x = col * config.TILE_SIZE + pos_x + random.random()
        y = row * config.TILE_SIZE + pos_y + random.random() + 2
        vfx.append(Vfx(
          kind="spark",
          pos=(x, y),
          vel=(0, 0.25),
          color=Skill.get_color(soul.skill),
          anim=FrameAnim(
            duration=60,
            frame_count=3
          )
        ))
    soul.pos = (pos_x, pos_y)

  def render(soul, anims):
    sprites = use_assets().sprites
    if not soul.obtaining and soul.time % 2:
      return None
    delay = Soul.ANIM_PERIOD // Soul.ANIM_FRAMES
    frame = soul.time % Soul.ANIM_PERIOD // delay
    frame = min(Soul.ANIM_FRAMES - 1, frame)
    sprite = sprites["soul" + str(frame)]
    if soul.skill:
      color = Skill.get_color(soul.skill)
      sprite = replace_color(sprite, palette.BLACK, color)
    return sprite
