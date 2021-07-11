from contexts import Context
from cores.knight import Knight
from anims.walk import WalkAnim
from config import WINDOW_WIDTH, WINDOW_HEIGHT
from assets import load as use_assets
from sprite import Sprite

class LoadingContext(Context):
  LOADING_TEXT = "Loading..."

  def __init__(ctx, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.anims = []
    ctx.knight = Knight(anims=[
      WalkAnim(period=30)
    ])

  def update(ctx):
    ctx.knight.update()

  def view(ctx):
    assets = use_assets()
    knight_sprite = ctx.knight.view()[0]
    knight_x = WINDOW_WIDTH - 16
    knight_y = WINDOW_HEIGHT - 16
    knight_sprite.pos = (knight_x, knight_y)
    knight_sprite.origin = ("right", "bottom")
    text_width = assets.ttf["roman"].width(LoadingContext.LOADING_TEXT)
    text_image = assets.ttf["roman"].render(LoadingContext.LOADING_TEXT)
    text_x = knight_x - knight_sprite.image.get_width() - 4
    text_y = knight_y - knight_sprite.image.get_height() // 2 + 4
    text_sprite = Sprite(
      image=text_image,
      pos=(text_x, text_y),
      origin=("right", "center")
    )
    return [text_sprite, knight_sprite]
