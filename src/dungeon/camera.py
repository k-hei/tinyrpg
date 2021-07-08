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

  def get_rect(camera):
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

  def focus(camera, cell, speed=None, force=False):
    if camera.flag and not force:
      return
    camera.flag = cell
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
    view_width, view_height = camera.size
    hero = game.hero
    focus_x, focus_y = hero.cell
    hero_x, hero_y = hero.cell
    hero_y -= hero.elev

    anims = []
    if len(game.anims):
      anims = game.anims[0]

    camera_speed = 4
    if camera.flag:
      focus_x, focus_y = camera.flag
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
        hero_x, hero_y = move_anim.cell

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
    else:
      move_anim = next((a for a in anims if (
        not a.done
        and a.target is hero
        and isinstance(a, MoveAnim)
      )), None)
      if move_anim:
        focus_x, focus_y = move_anim.cell

    camera_anim = camera.anims[0] if camera.anims else None
    if camera_anim:
      t = ease_out(camera_anim.update())
      start, end = camera_anim.target
      start_x, start_y = start
      end_x, end_y = end
      camera_x = lerp(start_x, end_x, t)
      camera_y = lerp(start_y, end_y, t)
      focus_x, focus_y = camera.flag
      if camera_anim.done:
        camera.anims.remove(camera_anim)
    else:
      camera_x, camera_y = camera.upscale((focus_x, focus_y))
      if camera.pos:
        old_camera_x, old_camera_y = camera.pos
        camera_speed = camera.speed or camera_speed
        camera_x = old_camera_x + (camera_x - old_camera_x) / camera_speed
        camera_y = old_camera_y + (camera_y - old_camera_y) / camera_speed
    camera.pos = (camera_x, camera_y)
    camera.cell = (focus_x, focus_y)
