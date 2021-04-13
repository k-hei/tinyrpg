import config
from anims.move import MoveAnim

MAX_RADIUS_X = 3
MAX_RADIUS_Y = 1

class Camera:
  def __init__(camera, size):
    camera.size = size
    camera.pos = None

  def reset(camera):
    camera.pos = None

  def update(camera, game):
    view_width, view_height = camera.size
    hero = game.hero
    hero_x, hero_y = hero.cell
    focus_x, focus_y = hero.cell

    anims = []
    if len(game.anims):
      anims = game.anims[0]

    CAMERA_SPEED = 8
    if game.room:
      focus_x, focus_y = game.room.get_center()
      CAMERA_SPEED = 16

      if game.room.get_width() > MAX_RADIUS_X * 2 + 1:
        for anim in anims:
          if anim.target is hero and type(anim) is MoveAnim and not anim.done:
            hero_x, _ = anim.cur_cell
            break
        if focus_x - hero_x > MAX_RADIUS_X:
          focus_x -= MAX_RADIUS_X
        elif hero_x - focus_x > MAX_RADIUS_X:
          focus_x += MAX_RADIUS_X
        else:
          focus_x = hero_x

      if game.room.get_height() > MAX_RADIUS_Y * 2 + 1:
        for anim in anims:
          if anim.target is hero and type(anim) is MoveAnim and not anim.done:
            _, hero_y = anim.cur_cell
            break
        if focus_y - hero_y > MAX_RADIUS_Y:
          focus_y -= MAX_RADIUS_Y
        elif hero_y - focus_y > MAX_RADIUS_Y:
          focus_y += MAX_RADIUS_Y
        else:
          focus_y = hero_y
    else:
      for anim in anims:
        if anim.target is hero and type(anim) is MoveAnim and not anim.done:
          focus_x, focus_y = anim.cur_cell
          break

    camera_x = (focus_x + 0.5) * config.tile_size - view_width / 2
    camera_y = (focus_y + 0.5) * config.tile_size - view_height / 2
    if camera.pos:
      old_camera_x, old_camera_y = camera.pos
      camera_x = old_camera_x + (camera_x - old_camera_x) / CAMERA_SPEED
      camera_y = old_camera_y + (camera_y - old_camera_y) / CAMERA_SPEED
    camera.pos = (camera_x, camera_y)
