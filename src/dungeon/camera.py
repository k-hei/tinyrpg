from math import ceil
import pygame
from pygame import Rect
from config import TILE_SIZE
from anims.move import MoveAnim
from anims.path import PathAnim
from anims.tween import TweenAnim
from easing.expo import ease_out
from lib.lerp import lerp

class Camera:
  MAX_RADIUS_X = 3
  MAX_RADIUS_Y = 2
  MOVE_DURATION = 15

  def __init__(camera, size):
    camera.size = size
    camera.pos = None
    camera.cell = None
    camera.flag = None
    camera.speed = None
    camera.anims = []

  def get_pos(camera):
    return camera.pos

  def get_size(camera):
    return camera.size

  def get_rect(camera, cell=None):
    if cell:
      x, y = camera.upscale(cell)
    else:
      x, y = camera.get_pos() or (0, 0)
    width, height = camera.get_size()
    return Rect(x, y, width, height)

  def reset(camera):
    camera.pos = None
    camera.blur()

  def upscale(camera, cell):
    width, height = camera.get_size()
    x, y = cell
    return (
      (x + 0.5) * TILE_SIZE - width / 2,
      (y + 0.5) * TILE_SIZE - height / 2
    )

  def focus(camera, cell, speed=None, force=False, tween=False, on_end=None):
    if camera.flag and not (force or tween):
      return
    camera.flag = cell
    if tween:
      camera.anims.append(TweenAnim(
        target=(camera.cell, cell),
        duration=speed,
        on_end=on_end
      ))
    else:
      camera.speed = speed

  def blur(camera):
    camera.flag = None
    camera.speed = None

  def is_cell_visible(camera, cell):
    col, row = cell
    center_col, center_row = camera.cell
    return (
      abs(col - center_col) <= Camera.MAX_RADIUS_X
      and abs(row - center_row) <= Camera.MAX_RADIUS_Y
    )

  def update(camera, game):
    camera_anim = camera.anims[0] if camera.anims else None
    if camera_anim:
      t = camera_anim.update()
      start, target = camera_anim.target
      start_x, start_y = start
      target_x, target_y = target
      camera_x = lerp(start_x, target_x, t)
      camera_y = lerp(start_y, target_y, t)
      camera_x, camera_y = camera.upscale((camera_x, camera_y))
      if camera_anim.done:
        camera.anims.remove(camera_anim)
    else:
      hero = game.hero
      if hero and hero.cell:
        focus_x, focus_y = hero.cell
        target_x, target_y = hero.cell
        hero_x, hero_y = hero.cell
        hero_y -= max(0, hero.elev)
      else:
        return

      anims = []
      if len(game.anims):
        anims = game.anims[0]

      camera_speed = 4
      if camera.flag:
        focus_x, focus_y = camera.flag
        target_x, target_y = camera.flag
        camera_speed = 20
      elif game.room:
        room = game.room
        focus_x, focus_y = room.get_center()
        camera_speed = 8
        move_anim = next((a for a in anims if (
          not a.done
          and a.target is hero
          and (type(a) is MoveAnim or type(a) is PathAnim)
        )), None)
        if move_anim:
          hero_x, hero_y, *hero_z = move_anim.cell
          hero_z = max(0, hero_z and hero_z[0] or 0)
          hero_y -= hero_z

        if hero and hero in game.floor.elems:
          room_halfwidth = ceil(room.get_width() / 2)
          room_halfheight = ceil(room.get_height() / 2)
          max_radius_x = room_halfwidth - Camera.MAX_RADIUS_X
          max_radius_y = room_halfheight - Camera.MAX_RADIUS_Y
          if room.get_width() > Camera.MAX_RADIUS_X * 2 + 1:
            if hero_x - focus_x < -max_radius_x:
              focus_x -= max_radius_x
            elif hero_x - focus_x > max_radius_x:
              focus_x += max_radius_x
            else:
              focus_x = hero_x

          if room.get_height() > Camera.MAX_RADIUS_Y * 2 + 1:
            if hero_y - focus_y < -max_radius_y:
              focus_y -= max_radius_y
            elif hero_y - focus_y > max_radius_y:
              focus_y += max_radius_y
            else:
              focus_y = hero_y

        target_x, target_y = focus_x, focus_y
      else:
        move_anim = next((a for a in anims if (
          not a.done
          and a.target is hero
          and isinstance(a, MoveAnim)
        )), None)
        if move_anim:
          focus_x, focus_y, *focus_z = move_anim.cell
          focus_z = max(0, focus_z and focus_z[0] or 0)
          focus_y -= focus_z
          target_x, target_y, target_z = move_anim.dest
          target_z = max(0, target_z and target_z[0] or 0)
          target_y -= target_z

      camera_x, camera_y = camera.upscale((focus_x, focus_y))
      if camera.pos:
        old_camera_x, old_camera_y = camera.pos
        camera_speed = camera.speed or camera_speed
        camera_x = old_camera_x + (camera_x - old_camera_x) / camera_speed
        camera_y = old_camera_y + (camera_y - old_camera_y) / camera_speed

    camera.pos = (camera_x, camera_y)
    camera.cell = (target_x, target_y)
