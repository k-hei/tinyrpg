from portraits import Portrait
from assets import load as use_assets
from anims.frame import FrameAnim

class MiraPortrait(Portrait):
  EYES_POS = (52, 38)
  MOUTH_POS = (61, 59)
  BLINK_INTERVAL = 150
  BLINK_DURATION = 16
  BLINK_FRAMES = ["mira_eyes", "mira_eyes_closing", "mira_eyes_closed", "mira_eyes_closing"]
  TALK_DURATION = 16
  TALK_FRAMES = ["mira_mouth", "mira_mouth_opening", "mira_mouth_open", "mira_mouth_opening"]

  class BlinkAnim(FrameAnim):
    def __init__(anim, *args, **kwargs):
      super().__init__(
        frames=MiraPortrait.BLINK_FRAMES,
        duration=MiraPortrait.BLINK_DURATION,
        *args, **kwargs
      )

  class TalkAnim(FrameAnim):
    def __init__(anim, *args, **kwargs):
      super().__init__(
        frames=MiraPortrait.TALK_FRAMES,
        duration=MiraPortrait.TALK_DURATION,
        *args, **kwargs
      )

  def __init__(portrait):
    portrait.talking = False
    portrait.anims = []
    portrait.ticks = 0

  def blink(portrait):
    portrait.anims.append(MiraPortrait.BlinkAnim())

  def start_talk(portrait):
    portrait.talking = True
    portrait.anims.append(MiraPortrait.TalkAnim(on_end=portrait.start_talk))

  def stop_talk(portrait):
    portrait.talking = False
    talk_anim = next((a for a in portrait.anims if type(a) is MiraPortrait.TalkAnim), None)
    if talk_anim:
      portrait.anims.remove(talk_anim)

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

    blink_anim = next((a for a in portrait.anims if type(a) is MiraPortrait.BlinkAnim), None)
    eyes_frame = blink_anim.frame if blink_anim else "mira_eyes"
    image.blit(assets[eyes_frame], MiraPortrait.EYES_POS)

    talk_anim = next((a for a in portrait.anims if type(a) is MiraPortrait.TalkAnim), None)
    mouth_frame = talk_anim.frame if talk_anim else "mira_mouth"
    image.blit(assets[mouth_frame], MiraPortrait.MOUTH_POS)

    return image
