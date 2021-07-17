from math import sin, cos, pi
import pygame
from pygame import Rect
from portraits import Portrait
from assets import load as use_assets
from anims.frame import FrameAnim
from colors.palette import BLUE, DARKBLUE
from lib.lerp import lerp

FRAME_PREFIX = "portrait_mira"

class MiraPortrait(Portrait):
  EYES_POS = (52, 38)
  MOUTH_POS = (61, 59)
  SHINE_POS = (144, 96)
  BLINK_INTERVAL = 150

  class BlinkAnim(FrameAnim):
    frames = [FRAME_PREFIX + "_eyes", FRAME_PREFIX + "_eyes_closing", FRAME_PREFIX + "_eyes_closed", FRAME_PREFIX + "_eyes_closing"]
    duration = 16

  class TalkAnim(FrameAnim):
    frames = [FRAME_PREFIX + "_mouth", FRAME_PREFIX + "_mouth_opening", FRAME_PREFIX + "_mouth_open", FRAME_PREFIX + "_mouth_opening"]
    duration = 16

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

  def render(portrait):
    portrait.update()
    assets = use_assets().sprites
    surface = assets[FRAME_PREFIX].copy()

    blink_anim = next((a for a in portrait.anims if type(a) is MiraPortrait.BlinkAnim), None)
    eyes_frame = blink_anim.frame() if blink_anim else FRAME_PREFIX + "_eyes"
    surface.blit(assets[eyes_frame], MiraPortrait.EYES_POS)

    talk_anim = next((a for a in portrait.anims if type(a) is MiraPortrait.TalkAnim), None)
    mouth_frame = talk_anim.frame() if talk_anim else FRAME_PREFIX + "_mouth"
    surface.blit(assets[mouth_frame], MiraPortrait.MOUTH_POS)

    ticks = portrait.ticks // 2 * 2

    BALL_WIDTH = 43
    BALL_HEIGHT = 17
    BALL_X = surface.get_width() - BALL_WIDTH
    BALL_Y = surface.get_height() - BALL_HEIGHT
    pygame.draw.rect(surface, DARKBLUE, Rect(BALL_X, BALL_Y, BALL_WIDTH, BALL_HEIGHT))
    for i in range(BALL_WIDTH):
      swing = sin(ticks % 600 / 600 * 2 * pi)
      amplitude = (sin(ticks % 240 / 240 * 2 * pi) + 1) / 2
      amplitude = lerp(3, 9, amplitude)
      height = (sin((ticks % 90 / 90 * 2 + swing + i / BALL_WIDTH) * 2 * pi) + 1) / 2
      height *= amplitude
      pygame.draw.rect(surface, DARKBLUE, Rect(
        (BALL_X + i, BALL_Y - int(height)),
        (1, int(height))
      ))

    BALL_HEIGHT //= 2
    BALL_Y = surface.get_height() - BALL_HEIGHT
    pygame.draw.rect(surface, BLUE, Rect(BALL_X, BALL_Y, BALL_WIDTH, BALL_HEIGHT))
    for i in range(BALL_WIDTH):
      swing = cos(ticks % 600 / 600 * 2 * pi)
      amplitude = (cos(ticks % 240 / 240 * 2 * pi) + 1) / 2
      amplitude = lerp(3, 9, amplitude)
      height = (cos((ticks % 90 / 90 * 2 + swing + (BALL_WIDTH - i) / BALL_WIDTH) * 2 * pi) + 1) / 2
      height *= amplitude
      pygame.draw.rect(surface, BLUE, Rect(
        (BALL_X + i, BALL_Y - int(height)),
        (1, int(height))
      ))

    shine_image = assets[FRAME_PREFIX + "_shine"]
    surface.blit(shine_image, MiraPortrait.SHINE_POS)

    hand_image = assets[FRAME_PREFIX + "_hand"]
    surface.blit(hand_image, (
      surface.get_width() - hand_image.get_width() - 19,
      surface.get_height() - hand_image.get_height()
    ))
    return surface
