from assets import load as use_assets
from contexts import Context
from comps.bar import Bar
from comps.skill import Skill
from skills import get_skill_text
from filters import replace_color, recolor, outline
from text import render as render_text
import pygame
from pygame import Rect
import palette
import keyboard
from comps.piece import Piece

from actors.knight import Knight
from actors.mage import Mage

from anims.tween import TweenAnim
from easing.expo import ease_out
from lerp import lerp

SPACING_X = 4
SPACING_Y = 4
SKILL_MARGIN_Y = 1
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
  def __init__(ctx, parent, on_close=None):
    super().__init__(parent)
    ctx.on_close = on_close
    ctx.char = parent.hero
    ctx.char_drawn = ctx.char
    ctx.index = 0
    ctx.index_drawn = -1
    ctx.offset = 0
    ctx.cursor = (0, 0)
    ctx.cursor_drawn = ctx.cursor
    ctx.arrange = False
    ctx.arrange_drawn = ctx.arrange
    ctx.pieces = parent.skill_builds[ctx.char]
    ctx.matrix_size = (3, 3)
    ctx.anims = []
    ctx.bar = Bar()
    ctx.enter()

  def enter(ctx):
    ctx.bar.enter()
    ctx.update_bar()
    ctx.anims.append([
      EnterAnim(duration=10, target="Deck"),
      EnterAnim(duration=10, target="Knight"),
      EnterAnim(duration=10, delay=4, target="Mage")
    ])
    for i, skill in enumerate(ctx.get_char_skills()):
      ctx.anims[0].append(EnterAnim(
        duration=10,
        delay=i * 6,
        target=skill
      ))
    game = ctx.parent
    build = game.skill_builds[ctx.char]
    for i, (skill, cell) in enumerate(build):
      ctx.anims[0].append(PlaceAnim(
        duration=ANIM_PLACE_DURATION,
        delay=i * ANIM_PLACE_STAGGER,
        target=skill.blocks
      ))

  def update_bar(ctx):
    skill = ctx.get_selected_skill()
    skill_text = get_skill_text(skill)
    ctx.bar.print(skill_text)

  def get_char_skills(ctx, char=None):
    return [s for s in ctx.parent.skill_pool if type(char or ctx.char) in s.users]

  def get_selected_skill(ctx):
    return ctx.get_char_skills()[ctx.index]

  def is_skill_used(ctx, skill):
    game = ctx.parent
    return skill in [skill for skill, cell in game.skill_builds[game.hero] + game.skill_builds[game.ally]]

  def is_cell_in_bounds(ctx, target):
    matrix_width, matrix_height = ctx.matrix_size
    x, y = target
    return x >= 0 and y >= 0 and x < matrix_width and y < matrix_height

  def is_cell_empty(ctx, target):
    for skill, cell in ctx.pieces:
      for block in Piece.offset(skill.blocks, cell):
        if block == target:
          return False
    return True

  def is_cell_valid(ctx, cell):
    return ctx.is_cell_in_bounds(cell) and ctx.is_cell_empty(cell)

  def handle_move_piece(ctx, delta):
    delta_x, delta_y = delta
    cursor_x, cursor_y = ctx.cursor
    new_cursor = (cursor_x + delta_x, cursor_y + delta_y)
    skill = ctx.get_selected_skill()
    for block in Piece.offset(skill.blocks, new_cursor):
      if not ctx.is_cell_in_bounds(block):
        break
    else:
      ctx.cursor = new_cursor

  def handle_place_piece(ctx):
    skill = ctx.get_selected_skill()
    for block in Piece.offset(skill.blocks, ctx.cursor):
      if not ctx.is_cell_empty(block):
        break
    else:
      ctx.pieces.append((skill, ctx.cursor))
      ctx.stop_arrange()
    ctx.anims.append([PlaceAnim(duration=ANIM_PLACE_DURATION, target=skill.blocks)])

  def handle_recall_piece(ctx):
    skill = ctx.get_selected_skill()
    ctx.anims.append([RecallAnim(duration=15, target=(skill, ctx.cursor))])
    ctx.stop_arrange()

  def stop_arrange(ctx):
    ctx.arrange = False
    ctx.cursor = (0, 0)

  def handle_swap_char(ctx):
    game = ctx.parent
    if ctx.char is game.hero:
      ctx.char = game.ally
    elif ctx.char is game.ally:
      ctx.char = game.hero
    ctx.pieces = game.skill_builds[ctx.char]
    ctx.index = 0
    ctx.offset = 0
    ctx.update_bar()

  def handle_move_index(ctx, delta):
    max_index = len(ctx.get_char_skills()) - 1
    old_index = ctx.index
    ctx.index += delta
    if ctx.index < 0:
      ctx.index = 0
    if ctx.index > max_index:
      ctx.index = max_index
    if ctx.index != old_index:
      ctx.update_bar()
    if ctx.index < ctx.offset:
      ctx.offset = ctx.index
    elif ctx.index > ctx.offset + SKILLS_VISIBLE - 1:
      ctx.offset = ctx.index - SKILLS_VISIBLE + 1

  def handle_select_piece(ctx):
    skill = ctx.get_selected_skill()
    if not ctx.is_skill_used(skill):
      ctx.arrange = True
      ctx.anims.append([CallAnim(duration=7, target=(skill, (0, 0)))])
      return
    game = ctx.parent
    ctx.arrange = True
    other = game.hero if ctx.char is game.ally else game.ally
    char_skills = [skill for skill, cell in game.skill_builds[ctx.char]]
    other_skills = [skill for skill, cell in game.skill_builds[other]]
    if skill in char_skills:
      index = char_skills.index(skill)
      build = game.skill_builds[ctx.char]
      _, cell = build.pop(index)
      ctx.cursor = cell
    elif skill in other_skills:
      index = other_skills.index(skill)
      build = game.skill_builds[other]
      build.pop(index)
      ctx.cursor = (0, 0)

  def handle_keydown(ctx, key):
    blocking = False
    for group in ctx.anims:
      for anim in group:
        if type(anim) in (EnterAnim, ExitAnim, CallAnim, RecallAnim):
          blocking = True
          break
    if blocking or keyboard.get_pressed(key) != 1:
      return

    if ctx.arrange:
      if key in keyboard.ARROW_DELTAS:
        ctx.handle_move_piece(delta=keyboard.ARROW_DELTAS[key])

      if key == pygame.K_RETURN or key == pygame.K_SPACE:
        ctx.handle_place_piece()

      if key == pygame.K_ESCAPE or key == pygame.K_BACKSPACE:
        ctx.handle_recall_piece()
    else:
      if key == pygame.K_TAB:
        ctx.handle_swap_char()

      if key == pygame.K_UP or key == pygame.K_w:
        ctx.handle_move_index(-1)

      if key == pygame.K_DOWN or key == pygame.K_s:
        ctx.handle_move_index(1)

      if key == pygame.K_RETURN or key == pygame.K_SPACE:
        ctx.handle_select_piece()

      if key == pygame.K_ESCAPE or key == pygame.K_BACKSPACE:
        ctx.close()

  def render(ctx):
    assets = use_assets()
    knight = assets.sprites["circle_knight"]
    mage = assets.sprites["circle_mage"]
    if type(ctx.char) is Knight:
      mage = replace_color(mage, palette.WHITE, palette.GRAY)
      mage = replace_color(mage, palette.BLUE, palette.BLUE_DARK)
    elif type(ctx.char) is Mage:
      knight = replace_color(knight, palette.WHITE, palette.GRAY)
      knight = replace_color(knight, palette.BLUE, palette.BLUE_DARK)
    deck = assets.sprites["deck"]
    tab = assets.sprites["deck_tab"]
    tab_inactive = replace_color(tab, palette.WHITE, palette.GRAY)
    skills = ctx.get_char_skills()
    skill = Skill.render(skills[0])

    tab_y = knight.get_height() + SPACING_Y
    deck_y = tab_y + tab.get_height() - TAB_OVERLAP
    surface = pygame.Surface((
      deck.get_width() + SPACING_X + skill.get_width() + SKILL_NUDGE_LEFT,
      deck_y + deck.get_height() + 1
    ))
    surface.set_colorkey(0xFF00FF)
    surface.fill(0xFF00FF)

    knight_scaled = knight
    knight_anim = ctx.anims and next((a for a in ctx.anims[0] if a.target == "Knight"), None)
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
    mage_anim = ctx.anims and next((a for a in ctx.anims[0] if a.target == "Mage"), None)
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

    skills = ctx.get_char_skills()
    skill_sel = ctx.get_selected_skill()
    entering = next((g for g in ctx.anims if (
      next((a for a in g if type(a) is EnterAnim), None)
    )), None)

    # handle skill select (TODO: refactor into input handler?)
    if not entering and ctx.index_drawn != ctx.index:
      # select the new skill
      ctx.anims.append([
        SelectAnim(
          duration=8,
          target=skills[ctx.index]
        )
      ])
      if ctx.index_drawn >= 0 and ctx.index_drawn < len(skills):
        # deselect the old skill
        ctx.anims[0].append(
          DeselectAnim(
            duration=6,
            target=skills[ctx.index_drawn]
          )
        )
      ctx.index_drawn = ctx.index

    # handle character switch (TODO: refactor into input handler?)
    if not entering and ctx.char_drawn != ctx.char:
      if not ctx.anims:
        ctx.anims.append([])
      for skill in skills:
        ctx.anims[0].append(ExitAnim(
          duration=6,
          target=skill
        ))
      skill_enters = []
      for i, skill in enumerate(ctx.get_char_skills()[:SKILLS_VISIBLE]):
        skill_enters.append(EnterAnim(
          duration=10,
          delay=i * 6,
          target=skill
        ))
      game = ctx.parent
      build = game.skill_builds[ctx.char]
      for i, (skill, cell) in enumerate(build):
        skill_enters.append(PlaceAnim(
          duration=ANIM_PLACE_DURATION,
          delay=i * ANIM_PLACE_STAGGER,
          target=skill.blocks
        ))
      ctx.anims.append(skill_enters)
      ctx.char_drawn = ctx.char
      ctx.index_drawn = -1

    # surface.blit(tab_inactive, (tab.get_width() - 1, tab_y))
    # surface.blit(tab_inactive, (tab.get_width() * 2 - 2, tab_y))
    deck_scaled = deck
    deck_anim = ctx.anims and next((a for a in ctx.anims[0] if type(a) is EnterAnim and a.target == "Deck"), None)
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

    if ctx.arrange and not ctx.arrange_drawn:
      ctx.cursor_drawn = ctx.cursor
    ctx.arrange_drawn = ctx.arrange

    cursor_x, cursor_y = ctx.cursor_drawn
    target_x, target_y = ctx.cursor

    if not deck_anim:
      # tab
      surface.blit(tab, (0, tab_y))
      text = render_text("1", assets.fonts["smallcaps"])
      surface.blit(text, (8, tab_y + 8))

      # grid
      grid_width, grid_height = ctx.matrix_size
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

      # pieces
      piece_anim = None
      in_range = abs(target_x - cursor_x) + abs(target_y - cursor_y) < 1
      for skill, (col, row) in ctx.pieces:
        offset = 0
        sprite = Piece.render(skill.blocks, Skill.get_color(skill), Skill.get_icon(skill))
        for group in ctx.anims:
          for anim in group:
            if type(anim) is PlaceAnim and anim.target is skill.blocks:
              piece_anim = anim
              break
        if piece_anim:
          if in_range:
            t = piece_anim.update()
            if piece_anim.time >= 0:
              offset = -4 * (1 - t)
            else:
              sprite = None
          else:
            offset = -4
        x = grid_x + col * Piece.BLOCK_SIZE
        y = grid_y + row * Piece.BLOCK_SIZE + offset
        if sprite:
          surface.blit(sprite, (x, y))

    pieces = []
    piece_anim = None
    for group in ctx.anims:
      for anim in group:
        if type(anim) in (CallAnim, RecallAnim):
          piece_anim = anim
          break
    if piece_anim:
      skill, (col, row) = piece_anim.target
      sprite = Piece.render(skill.blocks, Skill.get_color(skill_sel), Skill.get_icon(skill_sel))
      i = skills.index(skill)
      start_x = grid_x + col * Piece.BLOCK_SIZE
      start_y = grid_y + row * Piece.BLOCK_SIZE - 4
      end_x = deck.get_width() + SPACING_X
      end_y = deck_y + (i - ctx.offset) * (assets.sprites["skill"].get_height() + SKILL_MARGIN_Y)
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
    ctx.cursor_drawn = (cursor_x, cursor_y)
    if ctx.arrange and not piece_anim:
      blocks = skill_sel.blocks
      sprite = Piece.render(blocks, Skill.get_color(skill_sel), Skill.get_icon(skill_sel))
      surface.blit(sprite, (
        grid_x + cursor_x * Piece.BLOCK_SIZE,
        grid_y + cursor_y * Piece.BLOCK_SIZE - 4,
      ))

    if not entering:
      text = render_text("SKILL", assets.fonts["smallcaps"])
      text = recolor(text, palette.YELLOW)
      text = outline(text, (0, 0, 0))
      x = deck.get_width() + SPACING_X
      y = deck_y - text.get_height() - 2
      surface.blit(text, (x, y))

    badges = []
    visible_start = ctx.offset
    visible_end = SKILLS_VISIBLE + ctx.offset
    visible_skills = skills[visible_start:visible_end]
    for i, skill in enumerate(visible_skills):
      index = i + ctx.offset
      sprite = assets.sprites["skill"]
      x = deck.get_width() + SPACING_X
      y = deck_y + i * (sprite.get_height() + SKILL_MARGIN_Y)

      skill_sprite = sprite
      skill_anim = None
      for group in ctx.anims:
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
          if index == ctx.index:
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
        if ctx.arrange and index != ctx.index:
          sprite = Skill.render(skill, False)
        else:
          sprite = Skill.render(skill)

      if not skill_anim and not entering and index == ctx.index:
        subspr = sprite.subsurface(Rect(
          Skill.PADDING_X,
          Skill.PADDING_Y,
          sprite.get_width() - Skill.PADDING_X * 2,
          sprite.get_height() - Skill.PADDING_Y * 2
        ))
        sprite = replace_color(sprite, palette.WHITE, palette.YELLOW)
        sprite.blit(subspr, (Skill.PADDING_X, Skill.PADDING_Y))
        x += SKILL_NUDGE_LEFT

      if ctx.is_skill_used(skill) and (
        not skill_anim
        or type(skill_anim) in (SelectAnim, DeselectAnim)
      ):
        color = Skill.get_color(skill)
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

      y += skill_sprite.get_height() // 2 - sprite.get_height() // 2
      surface.blit(sprite, (x, y))

    for text, x, y in badges:
      surface.blit(text, (x, y))

    for sprite, x, y in pieces:
      surface.blit(sprite, (x, y))

    for group in ctx.anims:
      for anim in group:
        # piece animations are updated conditionally (TODO: consistency)
        if type(anim) is not PlaceAnim:
          anim.update()
        if anim.done:
          group.remove(anim)
      if not group:
        ctx.anims.remove(group)
    anim_group = ctx.anims[0] if ctx.anims else []

    return surface

  def draw(ctx, surface):
    assets = use_assets()
    sprite = ctx.render()
    surface.blit(sprite, (
      surface.get_width() // 2 - sprite.get_width() // 2 + SKILL_NUDGE_LEFT,
      (surface.get_height() - assets.sprites["statusbar"].get_height() - Bar.MARGIN * 2) // 2 - sprite.get_height() // 2
    ))
    ctx.bar.draw(surface)
