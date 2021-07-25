from contexts import Context
from cores.knight import Knight
from anims.walk import WalkAnim
from anims.jump import JumpAnim
from anims.pause import PauseAnim
from config import WINDOW_WIDTH, WINDOW_HEIGHT
from assets import load as use_assets
from sprite import Sprite
import pygame

class LoadingContext(Context):
  LOADING_TEXT = "Now Loading..."

  def __init__(ctx, loader, on_end, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.loader = loader
    ctx.on_end = on_end
    ctx.anims = []
    ctx.knight = Knight(anims=[
      WalkAnim(period=30)
    ])

  def update(ctx):
    ctx.knight.update()
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
      result = next(ctx.loader)
      if result is not None:
        ctx.loader = None
        ctx.anims = [PauseAnim(duration=30, on_end=lambda: (
          ctx.close(),
          ctx.on_end(result)
        ))]

  def view(ctx):
    if not ctx.loader:
      return []

    sprites = []
    assets = use_assets()

    knight_sprite = ctx.knight.view()[0]
    knight_image = knight_sprite.image
    knight_x = WINDOW_WIDTH - 16
    knight_y = WINDOW_HEIGHT - 16
    knight_sprite.pos = (knight_x, knight_y)
    knight_sprite.origin = ("right", "bottom")
    knight_sprite.layer = "ui"
    sprites.append(knight_sprite)

    label_font = assets.ttf["roman"]
    label_text = LoadingContext.LOADING_TEXT
    label_width = label_font.width(label_text)
    label_x = knight_x - knight_image.get_width() - 4 - label_width
    label_y = knight_y - knight_image.get_height() // 2
    for i, char in enumerate(label_text):
      char_image = label_font.render(char)
      char_y = label_y
      char_anim = next((a for a in ctx.anims if a.target == i), None)
      if char_anim:
        char_y += char_anim.offset
      sprites.append(Sprite(
        image=char_image,
        pos=(label_x, char_y),
        layer="ui"
      ))
      label_x += char_image.get_width()

    return sprites + super().view()
