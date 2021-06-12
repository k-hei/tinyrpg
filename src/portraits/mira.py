from math import sin, cos, pi
import pygame
from pygame import Rect
from portraits import Portrait
from assets import load as use_assets
from anims.frame import FrameAnim
from palette import BLUE, BLUE_DARK
from lib.lerp import lerp

class MiraPortrait(Portrait):
  EYES_POS = (52, 38)
  MOUTH_POS = (61, 59)
  SHINE_POS = (144, 96)
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
    surface = assets["mira"].copy()

    blink_anim = next((a for a in portrait.anims if type(a) is MiraPortrait.BlinkAnim), None)
    eyes_frame = blink_anim.frame if blink_anim else "mira_eyes"
    surface.blit(assets[eyes_frame], MiraPortrait.EYES_POS)

    talk_anim = next((a for a in portrait.anims if type(a) is MiraPortrait.TalkAnim), None)
    mouth_frame = talk_anim.frame if talk_anim else "mira_mouth"
    surface.blit(assets[mouth_frame], MiraPortrait.MOUTH_POS)

    BALL_WIDTH = 43
    BALL_HEIGHT = 17
    BALL_X = surface.get_width() - BALL_WIDTH
    BALL_Y = surface.get_height() - BALL_HEIGHT
    pygame.draw.rect(surface, BLUE_DARK, Rect(BALL_X, BALL_Y, BALL_WIDTH, BALL_HEIGHT))
    for i in range(BALL_WIDTH):
      swing = sin(portrait.ticks % 600 / 600 * 2 * pi)
      amplitude = (sin(portrait.ticks % 240 / 240 * 2 * pi) + 1) / 2
      amplitude = lerp(3, 9, amplitude)
      height = (sin((portrait.ticks % 90 / 90 * 2 + swing + i / BALL_WIDTH) * 2 * pi) + 1) / 2
      height *= amplitude
      pygame.draw.rect(surface, BLUE_DARK, Rect(
        (BALL_X + i, BALL_Y - int(height)),
        (1, int(height))
      ))

    BALL_HEIGHT //= 2
    BALL_Y = surface.get_height() - BALL_HEIGHT
    pygame.draw.rect(surface, BLUE, Rect(BALL_X, BALL_Y, BALL_WIDTH, BALL_HEIGHT))
    for i in range(BALL_WIDTH):
      swing = cos(portrait.ticks % 600 / 600 * 2 * pi)
      amplitude = (cos(portrait.ticks % 240 / 240 * 2 * pi) + 1) / 2
      amplitude = lerp(3, 9, amplitude)
      height = (cos((portrait.ticks % 90 / 90 * 2 + swing + (BALL_WIDTH - i) / BALL_WIDTH) * 2 * pi) + 1) / 2
      height *= amplitude
      pygame.draw.rect(surface, BLUE, Rect(
        (BALL_X + i, BALL_Y - int(height)),
        (1, int(height))
      ))

    shine_image = assets["mira_shine"]
    surface.blit(shine_image, MiraPortrait.SHINE_POS)

    hand_image = assets["mira_hand"]
    surface.blit(hand_image, (
      surface.get_width() - hand_image.get_width() - 19,
      surface.get_height() - hand_image.get_height()
    ))
    return surface
