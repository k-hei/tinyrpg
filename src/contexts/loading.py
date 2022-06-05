from pygame import Surface
from random import choice

from lib.sprite import Sprite
import assets
import debug
from contexts import Context

from cores.knight import Knight
from cores.mage import Mage
from cores.mouse import Mouse
from cores.bunny import Bunny

from anims.jump import JumpAnim
from anims.pause import PauseAnim
from colors.palette import BLACK
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_SIZE


def get_actor():
  LOADING_ACTORS = (Knight, Mage, Mouse, Bunny)
  Actor = choice(LOADING_ACTORS)
  return Actor(anims=[
    Actor.WalkAnim(period=2 * Actor.WalkAnim.period)
  ])

class LoadingContext(Context):
  LOADING_TEXT = "Now Loading..."
  LOADING_ACTORS = (Knight, Mage, Mouse)

  def __init__(ctx, loader, on_end, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.loader = loader
    ctx.on_end = on_end
    ctx.result = None
    ctx.anims = []
    ctx.actor = get_actor()

  def enter(ctx):
    ctx.get_head().loading = True

  def exit(ctx):
    ctx.get_head().loading = False
    ctx.close()
    ctx.on_end(ctx.result)

  def update(ctx):
    ctx.actor.update()
    anims = [a for a in ctx.anims if not a.done]
    if not anims:
      if not ctx.anims or type(ctx.anims[0]) is PauseAnim:
        ctx.anims = [JumpAnim(
          target=i,
          height=4,
          duration=15,
          delay=i * 4,
        ) for i in range(len(LoadingContext.LOADING_TEXT))]
      else:
        ctx.anims = [PauseAnim(duration=60)]
    for anim in ctx.anims:
      anim.update()
      if type(anim) is PauseAnim and anim.done:
        ctx.anims.remove(anim)

    if ctx.loader:
      try:
        result, *message = next(ctx.loader)
        message and message[0] and debug.log(*message)
        ctx.result = result
      except StopIteration:
        ctx.loader = None
        ctx.anims = [PauseAnim(duration=30, on_end=ctx.exit)]

  def view(ctx):
    if not ctx.loader:
      return []

    sprites = []

    bg_image = Surface(WINDOW_SIZE)
    bg_image.fill(BLACK)
    sprites.append(Sprite(image=bg_image))

    actor_sprite = ctx.actor.view()[0]
    actor_image = actor_sprite.image
    actor_x = WINDOW_WIDTH - 16
    actor_y = WINDOW_HEIGHT - 16
    actor_sprite.pos = (actor_x, actor_y)
    actor_sprite.origin = ("right", "bottom")
    actor_sprite.layer = "hud"
    sprites.append(actor_sprite)

    label_font = assets.ttf["normal"]
    label_text = LoadingContext.LOADING_TEXT
    label_width = label_font.width(label_text)
    label_x = actor_x - actor_image.get_width() - 4 - label_width
    label_y = actor_y - actor_image.get_height() // 2
    for i, char in enumerate(label_text):
      char_image = label_font.render(char)
      char_y = label_y
      char_anim = next((a for a in ctx.anims if a.target == i), None)
      if char_anim:
        char_y += char_anim.offset
      sprites.append(Sprite(
        image=char_image,
        pos=(label_x, char_y),
        layer="hud"
      ))
      label_x += char_image.get_width()

    return sprites + super().view()
