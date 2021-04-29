from comps.preview import Preview
from easing.expo import ease_out
from lib.lerp import lerp
from lib.cell import manhattan, is_adjacent
import pygame

from anims.tween import TweenAnim
from easing.expo import ease_out, ease_in_out
from lib.lerp import lerp

from dungeon.actors import DungeonActor
from dungeon.actors.mimic import Mimic

class EnterAnim(TweenAnim): pass
class ExitAnim(TweenAnim): pass
class SquishAnim(TweenAnim): pass
class ArrangeAnim(TweenAnim): pass

MARGIN = 8
SPACING = 4
LOG_HEIGHT = 48

class Previews:
  def __init__(self):
    self.previews = []
    self.enemies = []
    self.anims = []
    self.active = True

  def enter(self):
    self.active = True

  def exit(self):
    self.active = False

  def draw(self, surface, game):
    hero = game.hero
    floor = game.floor
    enemies = [e for e in floor.elems if (
      isinstance(e, DungeonActor)
      and not hero.allied(e)
      and e.cell in hero.visible_cells
      and not (type(e) is Mimic and e.idle)
    )]
    enemies.sort(key=lambda e: manhattan(e.cell, hero.cell))
    adjacent_enemies = [e for e in enemies if is_adjacent(e.cell, hero.cell)]
    if not self.enemies:
      self.enemies = enemies[:3]
    self.enemies = [e for e in self.enemies if e in enemies]
    new_enemies = [e for e in enemies if e not in self.enemies]
    if len(self.enemies) < 3 and new_enemies:
      while len(self.enemies) < 3 and new_enemies:
        self.enemies.append(new_enemies.pop(0))
    # if len(self.enemies) == 3 and adjacent_enemies:
    #   new_enemies = [e for e in adjacent_enemies if e not in self.enemies]
    #   if new_enemies:
    #     farthest = sorted(self.enemies, key=lambda e: manhattan(e.cell, hero.cell), reverse=True)
    #     for i, new_enemy in enumerate(new_enemies):
    #       index = self.enemies.index(farthest[i])
    #       self.enemies.pop(index)
    #       self.enemies.insert(index, new_enemy)

    entering = [a for a in self.anims if type(a) is EnterAnim]
    exiting = [a for a in self.anims if type(a) is ExitAnim or type(a) is SquishAnim]
    arranging = [a for a in self.anims if type(a) is ArrangeAnim]

    # exit
    if not entering:
      added = 0
      for preview in self.previews:
        if preview is None:
          continue
        exit_anim = next((a for a in exiting if a.target is preview), None)
        if exit_anim is None and (
          not self.active
          or not preview.actor in self.enemies
        ):
          Anim = ExitAnim if preview.actor.get_hp() else SquishAnim
          anim = Anim(
            duration=7,
            delay=added * 4,
            target=preview
          )
          self.anims.append(anim)
          exiting.append(anim)
          added += 1

    exited = False
    for anim in self.anims:
      if anim.done:
        self.anims.remove(anim)
        if type(anim) is ExitAnim or type(anim) is SquishAnim:
          index = self.previews.index(anim.target)
          self.previews.pop(index)
          self.previews.insert(index, None)
          exiting.remove(anim)
          exited = True
        elif type(anim) is ArrangeAnim:
          arranging.remove(anim)
        continue
      t = anim.update()
      if type(anim) is EnterAnim or type(anim) is ExitAnim:
        preview = anim.target
        sprite = preview.sprite or preview.render()
        if type(anim) is EnterAnim:
          t = ease_out(t)
        elif type(anim) is ExitAnim:
          t = 1 - t
        start_x = 0
        end_x = MARGIN + sprite.get_width()
        preview.x = lerp(start_x, end_x, t)
      elif type(anim) is SquishAnim:
        preview = anim.target
        sprite = preview.sprite or preview.render()
        preview.width = lerp(sprite.get_width(), sprite.get_width() * 2, t)
        preview.height = lerp(sprite.get_height(), 0, t)
      elif type(anim) is ArrangeAnim:
        for preview, (src, tgt) in anim.target.items():
          t = ease_in_out(t)
          start_y = src
          end_y = tgt
          preview.y = lerp(start_y, end_y, t)

    if not exiting and not self.active:
      self.previews = [p for p in self.previews if p]

    # enter
    if self.active and not exiting and (not arranging or exited):
      added = 0
      for enemy in self.enemies:
        preview = next((p for p in self.previews if p and p.actor is enemy), None)
        if preview is None and len(self.previews) < 3:
          preview = Preview(enemy)
          # self.previews.insert(self.enemies.index(preview.actor), preview)
          if self.enemies.index(preview.actor) == 0:
            self.previews.insert(0, preview)
          else:
            self.previews.append(preview)
          anim = EnterAnim(
            duration=15,
            delay=added * 10,
            target=preview
          )
          self.anims.append(anim)
          entering.append(anim)
          added += 1

    if exited and self.active:
      targets = {}
      def arrange_previews():
        for preview in self.previews:
          if preview is None or preview.actor not in self.enemies:
            continue
          cur_idx = self.previews.index(preview)
          tgt_idx = self.enemies.index(preview.actor)
          arrange_anim = None
          if arranging:
            arrange_anim = next((a for a in arranging if (
              0 in a.target
              and a.target[0] is preview
            )), None)
          if cur_idx != tgt_idx and arrange_anim is None:
            preview.y = cur_idx
            targets[preview] = (cur_idx, tgt_idx)
      arrange_previews()
      self.previews = [p for p in self.previews if p]
      arrange_previews()

      if targets:
        anim = ArrangeAnim(
          duration=15,
          target=targets
        )
        self.anims.append(anim)
        arranging.append(anim)

    window_width = surface.get_width()
    window_height = surface.get_height()
    for i in range(len(self.previews)):
      preview = self.previews[i]
      if preview is None:
        continue
      preview.update()
      sprite = preview.render()
      offset_x, offset_y = preview.offset
      x = window_width - preview.x + offset_x
      y = window_height - MARGIN - LOG_HEIGHT + offset_y
      delta = -SPACING - sprite.get_height()
      arrange_anim = arranging and preview in arranging[0].target
      if arrange_anim:
        y += delta * (preview.y + 1)
      else:
        y += delta * (i + 1)
      sprite_width = sprite.get_width()
      sprite_height = sprite.get_height()
      if preview.width != -1 or preview.height != -1:
        sprite = pygame.transform.scale(sprite, (int(preview.width), int(preview.height)))
      x += sprite_width // 2 - sprite.get_width() // 2
      y += sprite_height // 2 - sprite.get_height() // 2
      surface.blit(sprite, (x, y))
