from contexts import Context
from contexts.app import App
from assets import load as use_assets
from palette import WHITE
from anims.frame import FrameAnim

class MiraPortrait:
  EYES_POS = (52, 38)
  MOUTH_POS = (61, 59)
  BLINK_INTERVAL = 150
  BLINK_FRAMES = ["mira_eyes", "mira_eyes_closing", "mira_eyes_closed", "mira_eyes_closing"]
  TALK_FRAMES = ["mira_mouth", "mira_mouth_opening", "mira_mouth_open", "mira_mouth_opening"]

  class BlinkAnim(FrameAnim):
    def __init__(anim, *args, **kwargs):
      super().__init__(frames=MiraPortrait.BLINK_FRAMES, *args, **kwargs)

  class TalkAnim(FrameAnim): pass

  def __init__(portrait):
    portrait.anims = []
    portrait.ticks = 0

  def blink(portrait):
    portrait.anims.append(MiraPortrait.BlinkAnim(duration=16))

  # def start_talk(portrait):
  #   portrait.anims.append(MiraPortrait.TalkAnim(
  #   ))

  def update(portrait):
    for anim in portrait.anims:
      if anim.done:
        portrait.anims.remove(anim)
      else:
        anim.update()
    portrait.ticks += 1
    if portrait.ticks % MiraPortrait.BLINK_INTERVAL == 0:
      portrait.blink()

  def render(portrait):
    portrait.update()
    assets = use_assets().sprites
    image = assets["mira"].copy()
    image.blit(assets["mira_mouth"], MiraPortrait.MOUTH_POS)

    eyes_frame = "mira_eyes"
    eyes_anim = next((a for a in portrait.anims if type(a) is MiraPortrait.BlinkAnim), None)
    if eyes_anim:
      eyes_frame = eyes_anim.frame
    image.blit(assets[eyes_frame], MiraPortrait.EYES_POS)

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
