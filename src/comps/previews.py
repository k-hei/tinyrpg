from comps.preview import Preview
from easing.expo import ease_out
from lerp import lerp
from cell import manhattan
import pygame

from anims.tween import TweenAnim
from easing.expo import ease_out, ease_in_out
from lerp import lerp

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

    targets = [a.target for a in self.anims if a.target[0] != "Arrange"]
    entering = [preview for (kind, preview) in targets if kind == "Enter"]
    exiting = [preview for (kind, preview) in targets if kind == "Exit"]

    if not entering:
      added = 0
      for preview in self.previews:
        if preview.actor not in enemies and preview not in exiting:
          anim = TweenAnim(
            duration=6,
            delay=added * 4,
            target=("Exit", preview)
          )
          exiting.append(anim)
          self.anims.append(anim)
          added += 1

    if not exiting:
      added = 0
      for enemy in enemies:
        preview = next((p for p in self.previews if p.actor is enemy), None)
        if preview is None:
          preview = Preview(enemy)
          self.previews.append(preview)
          anim = TweenAnim(
            duration=15,
            delay=added * 10,
            target=("Enter", preview)
          )
          entering.append(anim)
          self.anims.append(anim)
          added += 1

    if not exiting and not entering:
      added = 0
      for preview in self.previews:
        cur_idx = self.previews.index(preview)
        tgt_idx = enemies.index(preview.actor)
        if cur_idx != tgt_idx:
          self.anims.append(TweenAnim(
            duration=15,
            delay=added * 10,
            target=("Arrange", preview, cur_idx, tgt_idx)
          ))
          added += 1

    for anim in self.anims:
      t = anim.update()
      kind = anim.target[0]
      if kind == "Enter" or kind == "Exit":
        kind, preview = anim.target
        if kind == "Enter":
          t = ease_out(t)
        elif kind == "Exit":
          t = 1 - t
        start_x = 0
        end_x = MARGIN + (preview.sprite or preview.render()).get_width()
        preview.x = lerp(start_x, end_x, t)
      elif kind == "Arrange":
        kind, preview, src, tgt = anim.target
        t = ease_in_out(t)
        start_y = src
        end_y = tgt
        preview.y = lerp(start_y, end_y, t)
      if anim.done:
        self.anims.remove(anim)
        if kind == "Exit":
          self.previews.remove(preview)

    window_width = surface.get_width()
    window_height = surface.get_height()
    arranges = [a for a in self.anims if a.target[0] == "Arrange"]
    for i in range(len(self.previews)):
      preview = self.previews[i]
      preview.update()
      sprite = preview.render()
      offset_x, offset_y = preview.offset
      x = window_width - preview.x + offset_x
      y = window_height - MARGIN - LOG_HEIGHT + offset_y
      delta = -SPACING - sprite.get_height()
      anim = next((a for a in arranges if a.target[1] is preview), None)
      if anim:
        y += delta * (preview.y + 1)
      else:
        y += delta * (i + 1)
      surface.blit(sprite, (x, y))
