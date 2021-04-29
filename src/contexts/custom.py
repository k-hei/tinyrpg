from assets import load as use_assets
from contexts import Context
from comps.bar import Bar
from comps.skill import Skill
from filters import replace_color, recolor, outline
from text import render as render_text
import pygame
from pygame import Rect
import palette
import keyboard
from comps.piece import Piece

from cores.knight import Knight
from cores.mage import Mage

from anims import Anim
from anims.tween import TweenAnim
from easing.expo import ease_out
from lib.lerp import lerp

SPACING_X = 4
SPACING_Y = 4
SKILL_SPACING = 1
SKILL_NUDGE_LEFT = 8
SKILLS_VISIBLE = 4
TAB_OVERLAP = 3
ANIM_PLACE_DURATION = 4
ANIM_PLACE_STAGGER = 4

class SkillAnim(TweenAnim): pass
class PieceAnim(TweenAnim): pass
class EnterAnim(SkillAnim): pass
class ExitAnim(SkillAnim): pass
class SelectAnim(SkillAnim): pass
class DeselectAnim(SkillAnim): pass
class PlaceAnim(PieceAnim): pass
class CallAnim(PieceAnim): pass
class RecallAnim(PieceAnim): pass

class CustomContext(Context):
  def __init__(menu, parent, pool, new_skills, builds, chars, on_close=None):
    super().__init__(parent)
    menu.pool = pool
    menu.new_skills = new_skills
    menu.builds = builds
    menu.chars = chars
    menu.on_close = on_close
    menu.char = chars[0]
    menu.char_drawn = menu.char
    menu.index = 0
    menu.index_drawn = -1
    menu.offset = 0
    menu.cursor = (0, 0)
    menu.cursor_drawn = menu.cursor
    menu.arrange = False
    menu.arrange_drawn = menu.arrange
    menu.pieces = builds[menu.char]
    menu.matrix_size = (3, 3)
    menu.anims = []
    menu.renders = 0
    menu.bar = Bar()
    menu.enter()

  def enter(menu):
    menu.bar.enter()
    menu.update_bar()
    menu.anims.append([
      EnterAnim(duration=10, target="Deck"),
      EnterAnim(duration=10, target="Knight"),
      EnterAnim(duration=10, delay=4, target="Mage")
    ])
    for i, skill in enumerate(menu.get_char_skills()):
      menu.anims[0].append(EnterAnim(
        duration=10,
        delay=i * 6,
        target=skill
      ))
    build = menu.builds[menu.char]
    for i, (skill, cell) in enumerate(build):
      menu.anims[0].append(PlaceAnim(
        duration=ANIM_PLACE_DURATION,
        delay=i * ANIM_PLACE_STAGGER,
        target=skill.blocks
      ))

  def update_bar(menu):
    skill = menu.get_selected_skill()
    if skill:
      menu.bar.print(skill.desc)
    else:
      menu.bar.print("Your skill pool is currently empty.")

  def get_char_skills(menu, char=None):
    if char is None:
      char = menu.char
    return [s for s in menu.pool if type(char) in s.users]

  def get_selected_skill(menu):
    skills = menu.get_char_skills()
    return skills[menu.index] if skills else None

  def is_skill_used(menu, skill):
    for char, build in menu.builds.items():
      for s, _ in build:
        if type(s) is type(skill):
          return True
    return False

  def is_cell_in_bounds(menu, target):
    matrix_width, matrix_height = menu.matrix_size
    x, y = target
    return x >= 0 and y >= 0 and x < matrix_width and y < matrix_height

  def is_cell_empty(menu, target):
    for skill, cell in menu.pieces:
      for block in Piece.offset(skill.blocks, cell):
        if block == target:
          return False
    return True

  def is_cell_valid(menu, cell):
    return menu.is_cell_in_bounds(cell) and menu.is_cell_empty(cell)

  def handle_move_piece(menu, delta):
    delta_x, delta_y = delta
    cursor_x, cursor_y = menu.cursor
    new_cursor = (cursor_x + delta_x, cursor_y + delta_y)
    skill = menu.get_selected_skill()
    for block in Piece.offset(skill.blocks, new_cursor):
      if not menu.is_cell_in_bounds(block):
        break
    else:
      menu.cursor = new_cursor

  def handle_place_piece(menu):
    skill = menu.get_selected_skill()
    for block in Piece.offset(skill.blocks, menu.cursor):
      if not menu.is_cell_empty(block):
        break
    else:
      menu.pieces.append((skill, menu.cursor))
      menu.stop_arrange()
      if skill in menu.new_skills:
        menu.new_skills.remove(skill)
    menu.anims.append([PlaceAnim(duration=ANIM_PLACE_DURATION, target=skill.blocks)])

  def handle_recall_piece(menu):
    skill = menu.get_selected_skill()
    menu.anims.append([RecallAnim(duration=15, target=(skill, menu.cursor))])
    menu.stop_arrange()

  def stop_arrange(menu):
    menu.arrange = False
    menu.cursor = (0, 0)

  def handle_swap_char(menu):
    if menu.char is menu.chars[0]:
      menu.char = menu.chars[1]
    elif menu.char is menu.chars[1]:
      menu.char = menu.chars[0]
    menu.pieces = menu.builds[menu.char]
    menu.index = 0
    menu.offset = 0
    menu.update_bar()

  def handle_move_index(menu, delta):
    skills = menu.get_char_skills()
    max_index = len(skills) - 1
    old_index = menu.index
    menu.index += delta
    if menu.index < 0:
      menu.index = 0
    if menu.index > max_index:
      menu.index = max_index
    if menu.index != old_index:
      menu.update_bar()
    if menu.index < menu.offset:
      menu.offset = menu.index
    elif menu.index > menu.offset + SKILLS_VISIBLE - 1:
      menu.offset = menu.index - SKILLS_VISIBLE + 1

  def handle_select_piece(menu):
    skill = menu.get_selected_skill()
    if not menu.is_skill_used(skill):
      menu.arrange = True
      menu.anims.append([CallAnim(duration=7, target=(skill, (0, 0)))])
      return
    menu.arrange = True
    other = menu.chars[0] if menu.char is menu.chars[1] else menu.chars[1]
    char_skills = [skill for skill, cell in menu.builds[menu.char]]
    other_skills = [skill for skill, cell in menu.builds[other]]
    if skill in char_skills:
      index = char_skills.index(skill)
      build = menu.builds[menu.char]
      _, cell = build.pop(index)
      menu.cursor = cell
    elif skill in other_skills:
      index = other_skills.index(skill)
      build = menu.builds[other]
      build.pop(index)
      menu.cursor = (0, 0)

  def handle_keydown(menu, key):
    blocking = False
    for group in menu.anims:
      for anim in group:
        if type(anim) in (EnterAnim, ExitAnim, CallAnim, RecallAnim):
          blocking = True
          break
    if blocking or keyboard.get_pressed(key) != 1:
      return

    if menu.arrange:
      if key in keyboard.ARROW_DELTAS:
        menu.handle_move_piece(delta=keyboard.ARROW_DELTAS[key])

      if key == pygame.K_RETURN or key == pygame.K_SPACE:
        menu.handle_place_piece()

      if key == pygame.K_ESCAPE or key == pygame.K_BACKSPACE:
        menu.handle_recall_piece()
    else:
      if key == pygame.K_TAB:
        menu.handle_swap_char()

      if key == pygame.K_UP or key == pygame.K_w:
        menu.handle_move_index(-1)

      if key == pygame.K_DOWN or key == pygame.K_s:
        menu.handle_move_index(1)

      if key == pygame.K_RETURN or key == pygame.K_SPACE:
        menu.handle_select_piece()

      if key == pygame.K_ESCAPE or key == pygame.K_BACKSPACE:
        menu.close()

  def render(menu):
    assets = use_assets()
    arrow = assets.sprites["arrow"]
    knight = assets.sprites["circle_knight"]
    mage = assets.sprites["circle_mage"]
    if type(menu.char) is Knight:
      mage = replace_color(mage, palette.WHITE, palette.GRAY)
      mage = replace_color(mage, palette.BLUE, palette.BLUE_DARK)
    elif type(menu.char) is Mage:
      knight = replace_color(knight, palette.WHITE, palette.GRAY)
      knight = replace_color(knight, palette.BLUE, palette.BLUE_DARK)
    deck = assets.sprites["deck"]
    tab = assets.sprites["deck_tab"]
    tab_inactive = replace_color(tab, palette.WHITE, palette.GRAY)
    skills = menu.get_char_skills()
    if skills:
      skill = Skill.render(skills[0])
    else:
      skill = assets.sprites["skill"]

    tab_y = knight.get_height() + SPACING_Y
    deck_y = tab_y + tab.get_height() - TAB_OVERLAP
    surface = pygame.Surface((
      deck.get_width() + SPACING_X + skill.get_width() + SKILL_NUDGE_LEFT,
      deck_y + deck.get_height() + 1 + SKILL_SPACING + arrow.get_height()
    ))
    surface.set_colorkey(0xFF00FF)
    surface.fill(0xFF00FF)

    knight_scaled = knight
    knight_anim = menu.anims and next((a for a in menu.anims[0] if a.target == "Knight"), None)
    if knight_anim:
      t = ease_out(knight_anim.pos)
      knight_scaled = pygame.transform.scale(knight, (
        int(knight.get_width() * t),
        knight.get_height()
      ))
    surface.blit(knight_scaled, (
      knight.get_width() // 2 - knight_scaled.get_width() // 2,
      0
    ))

    mage_scaled = mage
    mage_anim = menu.anims and next((a for a in menu.anims[0] if a.target == "Mage"), None)
    if mage_anim:
      t = ease_out(mage_anim.pos)
      mage_scaled = pygame.transform.scale(mage, (
        int(mage.get_width() * t),
        mage.get_height()
      ))
    surface.blit(mage_scaled, (
      knight.get_width() + SPACING_X + mage.get_width() // 2 - mage_scaled.get_width() // 2,
      0
    ))

    skills = menu.get_char_skills()
    skill_sel = menu.get_selected_skill()
    entering = next((g for g in menu.anims if (
      next((a for a in g if type(a) is EnterAnim), None)
    )), None)

    # handle skill select (TODO: refactor into input handler?)
    if skills and not entering and menu.index_drawn != menu.index:
      # select the new skill
      menu.anims.append([
        SelectAnim(
          duration=8,
          target=skills[menu.index]
        )
      ])
      if menu.index_drawn >= 0 and menu.index_drawn < len(skills):
        # deselect the old skill
        menu.anims[0].append(
          DeselectAnim(
            duration=6,
            target=skills[menu.index_drawn]
          )
        )
      menu.index_drawn = menu.index

    # handle character switch (TODO: refactor into input handler?)
    if not entering and menu.char_drawn != menu.char:
      if not menu.anims:
        menu.anims.append([])
      for skill in skills:
        menu.anims[0].append(ExitAnim(
          duration=6,
          target=skill
        ))
      skill_enters = []
      for i, skill in enumerate(menu.get_char_skills()[:SKILLS_VISIBLE]):
        skill_enters.append(EnterAnim(
          duration=10,
          delay=i * 6,
          target=skill
        ))
      build = menu.builds[menu.char]
      for i, (skill, cell) in enumerate(build):
        skill_enters.append(PlaceAnim(
          duration=ANIM_PLACE_DURATION,
          delay=i * ANIM_PLACE_STAGGER,
          target=skill.blocks
        ))
      menu.anims.append(skill_enters)
      menu.char_drawn = menu.char
      menu.index_drawn = -1

    # surface.blit(tab_inactive, (tab.get_width() - 1, tab_y))
    # surface.blit(tab_inactive, (tab.get_width() * 2 - 2, tab_y))
    deck_scaled = deck
    deck_anim = menu.anims and next((a for a in menu.anims[0] if type(a) is EnterAnim and a.target == "Deck"), None)
    if deck_anim:
      t = deck_anim.pos
      t = ease_out(t)
      width = deck.get_width()
      height = round(deck.get_height() * t)
      deck_scaled = pygame.transform.scale(deck, (width, height))

    surface.blit(deck_scaled, (
      0,
      deck_y + deck.get_height() // 2 - deck_scaled.get_height() // 2
    ))

    if menu.arrange and not menu.arrange_drawn:
      menu.cursor_drawn = menu.cursor
    menu.arrange_drawn = menu.arrange

    cursor_x, cursor_y = menu.cursor_drawn
    target_x, target_y = menu.cursor

    piece_anim = None
    for group in menu.anims:
      for anim in group:
        if type(anim) in (CallAnim, RecallAnim):
          piece_anim = anim
          break

    if not deck_anim:
      # tab
      surface.blit(tab, (0, tab_y))
      text = render_text("1", assets.fonts["smallcaps"])
      surface.blit(text, (8, tab_y + 8))

      # grid
      grid_width, grid_height = menu.matrix_size
      grid_x = deck.get_width() // 2 - grid_width * Piece.BLOCK_SIZE // 2
      grid_y = deck_y + deck.get_height() // 2 - grid_height * Piece.BLOCK_SIZE // 2
      for row in range(grid_width):
        for col in range(grid_height):
          x = col * Piece.BLOCK_SIZE + grid_x
          y = row * Piece.BLOCK_SIZE + grid_y
          pygame.draw.rect(surface, palette.GRAY_DARK, Rect(
            x, y,
            Piece.BLOCK_SIZE - 1, Piece.BLOCK_SIZE - 1
          ), 1)

      if menu.arrange and not piece_anim and menu.renders % 2:
        blocks = skill_sel.blocks
        sprite = Piece.render(blocks, (0, 0, 0, 0))
        surface.blit(sprite, (
          grid_x + target_x * Piece.BLOCK_SIZE,
          grid_y + target_y * Piece.BLOCK_SIZE
        ))

      # pieces
      place_anim = None
      in_range = abs(target_x - cursor_x) + abs(target_y - cursor_y) < 1
      for skill, (col, row) in menu.pieces:
        offset = 0
        sprite = Piece.render(skill.blocks, skill.color, Skill.get_icon(skill))
        for group in menu.anims:
          for anim in group:
            if type(anim) is PlaceAnim and anim.target is skill.blocks:
              place_anim = anim
              break
        if place_anim:
          if in_range:
            t = place_anim.update()
            if place_anim.time >= 0:
              offset = -4 * (1 - t)
            else:
              sprite = None
          else:
            offset = -4
        x = grid_x + col * Piece.BLOCK_SIZE + offset
        y = grid_y + row * Piece.BLOCK_SIZE + offset
        if sprite:
          surface.blit(sprite, (x, y))

    pieces = []
    if piece_anim:
      skill, (col, row) = piece_anim.target
      sprite = Piece.render(skill.blocks, skill.color, Skill.get_icon(skill_sel))
      i = skills.index(skill)
      start_x = grid_x + col * Piece.BLOCK_SIZE - 4
      start_y = grid_y + row * Piece.BLOCK_SIZE - 4
      end_x = deck.get_width() + SPACING_X
      end_y = deck_y + (i - menu.offset) * (assets.sprites["skill"].get_height() + SKILL_SPACING)
      t = ease_out(piece_anim.pos)
      if type(piece_anim) is CallAnim:
        t = 1 - t
      x = lerp(start_x, end_x, t)
      y = lerp(start_y, end_y, t)
      if type(piece_anim) is CallAnim or (
        piece_anim.time < piece_anim.duration // 2
        or piece_anim.time % 2
      ):
        pieces.append((sprite, x, y))

    # selected piece
    cursor_x += (target_x - cursor_x) / 4
    cursor_y += (target_y - cursor_y) / 4
    menu.cursor_drawn = (cursor_x, cursor_y)
    if menu.arrange and not piece_anim:
      blocks = skill_sel.blocks
      sprite = Piece.render(blocks, skill_sel.color, Skill.get_icon(skill_sel))
      surface.blit(sprite, (
        grid_x + cursor_x * Piece.BLOCK_SIZE - 4,
        grid_y + cursor_y * Piece.BLOCK_SIZE - 4,
      ))

    if not entering:
      text = render_text("SKILL", assets.fonts["smallcaps"])
      text = recolor(text, palette.YELLOW)
      text = outline(text, (0, 0, 0))
      x = deck.get_width() + SPACING_X
      y = deck_y - text.get_height() - SKILL_SPACING - 1
      surface.blit(text, (x, y))

    badges = []
    visible_start = menu.offset
    visible_end = menu.offset + SKILLS_VISIBLE
    visible_skills = skills[visible_start:visible_end]
    for i, skill in enumerate(visible_skills):
      index = i + menu.offset
      sprite = assets.sprites["skill"]
      x = deck.get_width() + SPACING_X
      y = deck_y + i * (sprite.get_height() + SKILL_SPACING)

      skill_sprite = sprite
      skill_anim = None
      for group in menu.anims:
        for anim in group:
          if anim.target is skill and isinstance(anim, SkillAnim):
            skill_anim = anim
            break
      if skill_anim and type(skill_anim) in (EnterAnim, ExitAnim):
        t = skill_anim.pos
        if type(skill_anim) is EnterAnim:
          t = ease_out(t)
        elif type(skill_anim) is ExitAnim:
          t = 1 - t
          if index == menu.index:
            x += SKILL_NUDGE_LEFT
        sprite = skill_sprite
        sprite = pygame.transform.scale(sprite, (
          sprite.get_width(),
          round(sprite.get_height() * t)
        ))
      else:
        if type(skill_anim) is SelectAnim:
          t = ease_out(skill_anim.pos)
          x += t * SKILL_NUDGE_LEFT
        if type(skill_anim) is DeselectAnim:
          t = 1 - skill_anim.pos
          x += t * SKILL_NUDGE_LEFT
        if menu.arrange and index != menu.index:
          sprite = Skill.render(skill, False)
        else:
          sprite = Skill.render(skill)

      if not skill_anim and not entering and index == menu.index:
        subspr = sprite.subsurface(Rect(
          Skill.PADDING_X,
          Skill.PADDING_Y,
          sprite.get_width() - Skill.PADDING_X * 2,
          sprite.get_height() - Skill.PADDING_Y * 2
        ))
        sprite = replace_color(sprite, palette.WHITE, palette.YELLOW)
        sprite.blit(subspr, (Skill.PADDING_X, Skill.PADDING_Y))
        x += SKILL_NUDGE_LEFT

      if not skill_anim or type(skill_anim) in (SelectAnim, DeselectAnim):
        if menu.is_skill_used(skill):
          color = skill.color
          subspr = sprite.subsurface(Rect(3, 3, sprite.get_width() - 6, sprite.get_height() - 6))
          subspr = replace_color(subspr, color, palette.darken(color))
          subspr = replace_color(subspr, palette.WHITE, palette.GRAY)
          sprite.blit(subspr, (3, 3))
          surface.blit(sprite, (x, y))
          if not entering:
            text = render_text("ON", assets.fonts["smallcaps"])
            text = recolor(text, palette.YELLOW)
            text = outline(text, (0, 0, 0))
            badges.append((text, x + sprite.get_width() - text.get_width() - 6, y + sprite.get_height() - 6))
        elif skill in menu.new_skills and not entering:
          text = render_text("NEW", assets.fonts["smallcaps"])
          text = recolor(text, palette.YELLOW if menu.renders % 60 >= 30 else palette.YELLOW_DARK)
          text = outline(text, (0, 0, 0))
          badges.append((text, x + sprite.get_width() - text.get_width() - 6, y + sprite.get_height() - 6))

      y += skill_sprite.get_height() // 2 - sprite.get_height() // 2
      surface.blit(sprite, (x, y))

    for text, x, y in badges:
      surface.blit(text, (x, y))

    for sprite, x, y in pieces:
      surface.blit(sprite, (x, y))

    skill_sprite = assets.sprites["skill"]
    if menu.renders % 30 >= 10:
      x = deck.get_width() + SPACING_X + skill_sprite.get_width() // 2  - arrow.get_width() // 2
      if menu.offset > 0:
        y = deck_y - arrow.get_height() - SKILL_SPACING - 1
        surface.blit(arrow, (x, y))

      if menu.offset + SKILLS_VISIBLE < len(skills):
        arrow = pygame.transform.flip(arrow, False, True)
        y = deck_y + SKILLS_VISIBLE * (skill_sprite.get_height() + SKILL_SPACING)
        surface.blit(arrow, (x, y))

    for group in menu.anims:
      for anim in group:
        # piece animations are updated conditionally (TODO: consistency)
        if type(anim) is not PlaceAnim:
          anim.update()
        if anim.done:
          group.remove(anim)
      if not group:
        menu.anims.remove(group)
    anim_group = menu.anims[0] if menu.anims else []

    menu.renders += 1
    return surface

  def draw(menu, surface):
    assets = use_assets()
    sprite = menu.render()
    bar_height = assets.sprites["statusbar"].get_height() + Bar.MARGIN * 2
    arrow_offset = assets.sprites["arrow"].get_height() + SKILL_SPACING
    x = surface.get_width() // 2 - sprite.get_width() // 2 + SKILL_NUDGE_LEFT
    y = (surface.get_height() - bar_height) // 2
    y -= (sprite.get_height() - arrow_offset) // 2
    surface.blit(sprite, (x, y))
    menu.bar.draw(surface)
