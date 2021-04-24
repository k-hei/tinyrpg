import config
import math
from anims.move import MoveAnim

class Camera:
  MAX_RADIUS_X = 2
  MAX_RADIUS_Y = 2

  def __init__(camera, size):
    camera.size = size
    camera.pos = None
    camera.cell = None
    camera.flag = None
    camera.speed = None

  def reset(camera):
    camera.pos = None

  def focus(camera, cell, speed=None):
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
    hero_x, hero_y = hero.cell
    focus_x, focus_y = hero.cell

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
      for anim in anims:
        if anim.target is hero and type(anim) is MoveAnim and not anim.done:
          hero_x, hero_y = anim.cur_cell
          break

      room_halfwidth = room.get_width() // 2 + 1
      room_halfheight = room.get_height() // 2 + 1
      max_radius_x = room_halfwidth - Camera.MAX_RADIUS_X
      max_radius_y = room_halfheight - Camera.MAX_RADIUS_Y
      if room.get_width() > Camera.MAX_RADIUS_X * 2 + 1:
        if hero_x - focus_x < -max_radius_x:
          focus_x -= max_radius_x
        elif hero_x - focus_x > max_radius_x:
          focus_x += max_radius_x
        else:
          focus_x = hero_x

      if room.get_height() > Camera.MAX_RADIUS_Y + 1:
        if hero_y - focus_y < -max_radius_y:
          focus_y -= max_radius_y
        elif hero_y - focus_y > max_radius_y:
          focus_y += max_radius_y
        else:
          focus_y = hero_y
    else:
      for anim in anims:
        if anim.target is hero and type(anim) is MoveAnim and not anim.done:
          focus_x, focus_y = anim.cur_cell
          break

    camera_speed = camera.speed or camera_speed
    camera_x = (focus_x + 0.5) * config.TILE_SIZE - view_width / 2
    camera_y = (focus_y + 0.5) * config.TILE_SIZE - view_height / 2
    if camera.pos:
      old_camera_x, old_camera_y = camera.pos
      camera_x = old_camera_x + (camera_x - old_camera_x) / camera_speed
      camera_y = old_camera_y + (camera_y - old_camera_y) / camera_speed
    camera.pos = (camera_x, camera_y)
    camera.cell = (focus_x, focus_y)
