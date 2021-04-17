from assets import load as use_assets
from contexts import Context
from comps.skill import Skill
from filters import replace_color
import pygame
from pygame import Rect
import palette
import keyboard

from actors.knight import Knight
from actors.mage import Mage

SPACING_X = 4
SPACING_Y = 4
SKILL_MARGIN_Y = 1
SKILL_NUDGE_LEFT = 8
TAB_OVERLAP = 3

class CustomContext(Context):
  def __init__(ctx, parent, on_close=None):
    super().__init__(parent)
    ctx.char = parent.hero
    ctx.index = 0
    ctx.on_close = on_close

  def handle_keydown(ctx, key):
    if keyboard.get_pressed(key) != 1:
      return

    if key == pygame.K_TAB:
      if ctx.char is ctx.parent.hero:
        ctx.char = ctx.parent.ally
      elif ctx.char is ctx.parent.ally:
        ctx.char = ctx.parent.hero

    if key == pygame.K_UP:
      ctx.index = max(0, ctx.index - 1)

    if key == pygame.K_DOWN:
      ctx.index = min(len(ctx.char.skills) - 1, ctx.index + 1)

    if key == pygame.K_ESCAPE:
      ctx.close()

  def render(ctx):
    assets = use_assets()
    circle_knight = assets.sprites["circle_knight"]
    circle_mage = assets.sprites["circle_mage"]
    if type(ctx.char) is Knight:
      circle_mage = replace_color(circle_mage, palette.WHITE, palette.GRAY)
      circle_mage = replace_color(circle_mage, palette.BLUE, palette.BLUE_DARK)
    elif type(ctx.char) is Mage:
      circle_knight = replace_color(circle_knight, palette.WHITE, palette.GRAY)
      circle_knight = replace_color(circle_knight, palette.BLUE, palette.BLUE_DARK)
    deck = assets.sprites["deck"]
    tab = assets.sprites["deck_tab"]
    tab_inactive = replace_color(tab, palette.WHITE, palette.GRAY)
    skill = Skill.render(ctx.char.skill)

    tab_y = circle_knight.get_height() + SPACING_Y
    deck_y = tab_y + tab.get_height() - TAB_OVERLAP
    surface = pygame.Surface((
      deck.get_width() + SPACING_X + skill.get_width() + SKILL_NUDGE_LEFT,
      deck_y + deck.get_height()
    ))
    surface.set_colorkey(0xFF00FF)
    surface.fill(0xFF00FF)
    surface.blit(circle_knight, (0, 0))
    surface.blit(circle_mage, (circle_knight.get_width() + SPACING_X, 0))

    surface.blit(tab_inactive, (tab.get_width() - 1, tab_y))
    surface.blit(tab_inactive, (tab.get_width() * 2 - 2, tab_y))
    surface.blit(deck, (0, deck_y))
    surface.blit(tab, (0, tab_y))

    y = deck_y
    for i, skill in enumerate(ctx.parent.skills[ctx.char]):
      sprite = Skill.render(skill)
      x = deck.get_width() + SPACING_X
      if i == ctx.index:
        subspr = sprite.subsurface(Rect(
          Skill.PADDING_X,
          Skill.PADDING_Y,
          sprite.get_width() - Skill.PADDING_X * 2,
          sprite.get_height() - Skill.PADDING_Y * 2
        ))
        sprite = replace_color(sprite, palette.WHITE, palette.YELLOW)
        sprite.blit(subspr, (Skill.PADDING_X, Skill.PADDING_Y))
        x += SKILL_NUDGE_LEFT
      surface.blit(sprite, (x, y))
      y += sprite.get_height() + SKILL_MARGIN_Y
    return surface

  def draw(ctx, surface):
    sprite = ctx.render()
    surface.fill(0x000000)
    surface.blit(sprite, (
      surface.get_width() // 2 - sprite.get_width() // 2 + SKILL_NUDGE_LEFT,
      surface.get_height() // 2 - sprite.get_height() // 2
    ))
