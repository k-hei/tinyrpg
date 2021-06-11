from contexts import Context
from contexts.app import App
from assets import load as use_assets
from palette import WHITE

class MiraPortrait:
  EYES_POS = (52, 38)
  MOUTH_POS = (61, 59)

  def __init__(portrait):
    pass

  def render(portrait):
    assets = use_assets().sprites
    image = assets["mira"].copy()
    image.blit(assets["mira_eyes"], MiraPortrait.EYES_POS)
    image.blit(assets["mira_mouth"], MiraPortrait.MOUTH_POS)
    return image

class PortraitContext(Context):
  def __init__(ctx):
    super().__init__()
    ctx.portrait = MiraPortrait()

  def draw(ctx, surface):
    surface.fill(WHITE)
    portrait = ctx.portrait.render()
    surface.blit(portrait, (0, 0))

App(
  size=(160, 128),
  title="mira portrait demo",
  context=PortraitContext()
).init()
