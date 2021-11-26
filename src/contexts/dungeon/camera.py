from math import ceil
from pygame import Rect
import lib.vector as vector
from dungeon.room import Blob as Room
from config import TILE_SIZE

class Camera:
  SPEED = 8
  MAX_XRADIUS = 3
  MAX_YRADIUS = 2

  def resolve_target_group(target_group):
    scale = TILE_SIZE
    room = None
    targets = []
    for target in target_group:
      if isinstance(target, Room):
        room = target
      else:
        targets.append(target.pos)
        scale = min(scale, target.scale)
    target = vector.mean(*targets)

    if room is None:
      return target

    target_x, target_y = target
    focus_x, focus_y = vector.scale(
      vector.add(room.center, (0.5, 0.5)),
      scale
    )

    max_xradius = (ceil(room.width / 2) - Camera.MAX_XRADIUS) * scale
    max_yradius = (ceil(room.height / 2) - Camera.MAX_YRADIUS) * scale

    if room.width > Camera.MAX_XRADIUS * 2 + 1:
      if target_x - focus_x < -max_xradius:
        focus_x -= max_xradius
      elif target_x - focus_x > max_xradius:
        focus_x += max_xradius
      else:
        focus_x = target_x

    if room.height > Camera.MAX_YRADIUS * 2 + 1:
      if target_y - focus_y < -max_yradius:
        focus_y -= max_yradius
      elif target_y - focus_y > max_yradius:
        focus_y += max_yradius
      else:
        focus_y = target_y

    return (focus_x, focus_y)

  def __init__(camera, size, pos=None):
    camera.size = size
    camera.pos = pos or None
    camera.vel = (0, 0)
    camera.target_groups = []

  @property
  def pos(camera):
    return camera._pos

  @pos.setter
  def pos(camera, pos):
    camera._pos = pos
    camera._rect = None

  @property
  def rect(camera):
    if camera._rect:
      return camera._rect

    if camera.pos is None:
      return None

    return Rect(
      vector.subtract(
        camera.pos,
        vector.scale(camera.size, 1 / 2)
      ),
      camera.size
    )

  @property
  def target(camera):
    return camera.target_groups[-1]

  @property
  def targets(camera):
    return [t for g in camera.target_groups for t in g]

  def focus(camera, target, force=False):
    if target in camera.targets:
      if force:
        camera.target_groups = [[target]]
      return

    if camera.target_groups and not force:
      camera.target_groups[-1].append(target)
    else:
      camera.target_groups.append([target])

    if not camera.pos:
      camera.pos = Camera.resolve_target_group(camera.target_groups[-1])

  def blur(camera, target=None):
    if target is None:
      camera.target = []
    elif target in camera.target:
      camera.target.remove(target)

  def update(camera):
    if not camera.pos or not camera.target_groups:
      return
    target_pos = Camera.resolve_target_group(camera.target_groups[-1])
    target_vel = vector.scale(vector.subtract(target_pos, camera.pos), 1 / Camera.SPEED * 8)
    camera.vel = vector.scale(vector.subtract(target_vel, camera.vel), 1 / 8)
    camera.pos = vector.add(camera.pos, camera.vel)
