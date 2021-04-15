from comps.preview import Preview
from easing.expo import ease_out
from lerp import lerp
from cell import manhattan
import pygame

from anims.tween import TweenAnim
from easing.expo import ease_out, ease_in_out
from lerp import lerp

class EnterAnim(TweenAnim): pass
class ExitAnim(TweenAnim): pass
class ArrangeAnim(TweenAnim): pass

MARGIN = 8
SPACING = 4
LOG_HEIGHT = 48

class Previews:
  def __init__(self):
    self.previews = []
    self.anims = []

  def draw(self, surface, game):
    hero = game.hero
    floor = game.floor
    is_valid_actor = lambda actor: (
      actor.faction == "enemy"
      and actor in floor.actors
      and actor.cell in hero.visible_cells
    )

    enemies = [a for a in floor.actors if is_valid_actor(a)]
    enemies.sort(key=lambda e: manhattan(e.cell, hero.cell))
    enemies = enemies[:3]

    entering = [a for a in self.anims if type(a) is EnterAnim]
    exiting = [a for a in self.anims if type(a) is ExitAnim]
    arranging = [a for a in self.anims if type(a) is ArrangeAnim]

    # exit
    if not entering:
      added = 0
      for preview in self.previews:
        if preview is None:
          continue
        exit_anim = next((a for a in exiting if a.target is preview), None)
        if exit_anim is None and preview.actor not in enemies:
          anim = ExitAnim(
            duration=6,
            delay=added * 4,
            target=preview
          )
          self.anims.append(anim)
          exiting.append(anim)
          added += 1

    # enter
    if not exiting and not arranging:
      added = 0
      for enemy in enemies:
        preview = next((p for p in self.previews if p and p.actor is enemy), None)
        if preview is None:
          preview = Preview(enemy)
          if None in self.previews:
            index = self.previews.index(None)
            self.previews.remove(None)
            self.previews.insert(index, preview)
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

    # arrange
    if not exiting and not entering:
      for preview in self.previews:
        if preview is None:
          continue
        cur_idx = self.previews.index(preview)
        tgt_idx = enemies.index(preview.actor)
        arrange_anim = next((a for a in arranging if a.target[0] is preview), None)
        if cur_idx != tgt_idx and arrange_anim is None:
          anim = ArrangeAnim(
            duration=15,
            target=(preview, cur_idx, tgt_idx)
          )
          self.anims.append(anim)
          arranging.append(anim)

    for anim in self.anims:
      t = anim.update()
      if type(anim) is EnterAnim or type(anim) is ExitAnim:
        preview = anim.target
        if type(anim) is EnterAnim:
          t = ease_out(t)
        elif type(anim) is ExitAnim:
          t = 1 - t
        start_x = 0
        end_x = MARGIN + (preview.sprite or preview.render()).get_width()
        preview.x = lerp(start_x, end_x, t)
      elif type(anim) is ArrangeAnim:
        preview, src, tgt = anim.target
        t = ease_in_out(t)
        start_y = src
        end_y = tgt
        preview.y = lerp(start_y, end_y, t)
      if anim.done:
        self.anims.remove(anim)
        if type(anim) is ExitAnim:
          index = self.previews.index(preview)
          self.previews.remove(preview)
          self.previews.insert(index, None)
        elif type(anim) is ArrangeAnim:
          preview, src, tgt = anim.target
          self.previews.remove(preview)
          self.previews.insert(tgt, preview)
          arranging.remove(anim)
          self.previews = [p for p in self.previews if p]

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
      arrange_anim = next((a for a in arranging if a.target[0] is preview), None)
      if arrange_anim:
        y += delta * (preview.y + 1)
      else:
        y += delta * (i + 1)
      surface.blit(sprite, (x, y))
