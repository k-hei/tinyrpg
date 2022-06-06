from dataclasses import dataclass
from math import ceil
from pygame import Rect
import lib.vector as vector
from dungeon.room import Blob as Room
from anims.tween import TweenAnim
from config import TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT
import debug


@dataclass
class CameraConstraints:
  left: int = 0
  right: int = 0
  top: int = 0
  bottom: int = 0

  @property
  def width(constraints):
    return abs(constraints.right - constraints.left)

  @property
  def height(constraints):
    return abs(constraints.bottom - constraints.top)

class Camera:
  SPEED = 8
  MAX_XRADIUS = 3
  MAX_YRADIUS = 2

  def resolve_target_group(target_group, camera_offset=(0, 0)):
    scale = TILE_SIZE
    room = None
    target = None
    targets = []
    for t in target_group:
      if isinstance(t, Room):
        room = t
      elif type(t) is tuple:
        targets.append(vector.subtract(t, camera_offset))
        target = t
      else:
        targets.append(t.pos)
        target = t
        scale = min(scale, target.scale)

    if targets:
      target = vector.mean(*targets)

    if room is None:
      return target

    focus_x, focus_y = vector.scale(
      vector.add(room.center, (0.5, 0.5)),
      scale
    )

    if target:
      target_x, target_y = target
    else:
      return (focus_x, focus_y)

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

  def __init__(camera, size, pos=None, offset=(0, 0), constraints=None):
    camera.size = size
    camera.pos = pos
    camera.offset = offset
    camera.constraints = constraints
    camera.vel = (0, 0)
    camera.target_groups = []
    camera.anim = None

  @property
  def pos(camera):
    return (vector.add(camera._pos, camera.offset)
      if camera._pos and camera.offset
      else camera._pos)

  @pos.setter
  def pos(camera, pos):
    camera._pos = pos
    camera._rect = None

  @property
  def rect(camera):
    if not camera._rect and camera.pos:
      camera._rect = Rect(
        vector.subtract(
          camera.pos,
          vector.scale(camera.size, 1 / 2)
        ),
        camera.size
      )
    return camera._rect

  @property
  def target(camera):
    return camera.target_groups[-1] if camera.target_groups else []

  @property
  def targets(camera):
    return [t for g in camera.target_groups for t in g]

  def is_pos_beyond_yrange(camera, pos):
    _, target_y = pos
    _, camera_y = camera.pos
    return target_y - camera_y <= -WINDOW_HEIGHT / 2 + TILE_SIZE

  def focus(camera, target, force=False, anim=None, instant=False):
    if type(target) is list and force:
      camera.target_groups = [target]
    elif target in camera.targets:
      if not force:
        return
      camera.target_groups = [[target]]
    elif camera.target_groups and not force:
      camera.target_groups[-1].append(target)
    else:
      camera.target_groups.append([target])

    target_pos = Camera.resolve_target_group(camera.target_groups[-1], camera.offset)

    if not camera.pos or instant:
      camera.pos = target_pos
    elif anim:
      anim.target = (camera.pos, target_pos)
      camera.anim = anim

  def tween(camera, target, duration=None, on_end=None):
    start_pos = camera.pos
    camera.focus(target, force=True)
    goal_pos = Camera.resolve_target_group(camera.target_groups[-1], camera.offset)

    if not start_pos:
      camera.pos = vector.add(goal_pos, camera.offset)
      return

    duration = duration or int(vector.distance(start_pos, goal_pos) / 4)
    camera.anim = TweenAnim(
      target=(start_pos, goal_pos),
      duration=duration,
      on_end=on_end
    )
    return duration

  def blur(camera, target=None):
    if target is None:
      camera.target_groups.pop()
      return

    if target in camera.target:
      camera.target.remove(target)
      if not camera.target:
        camera.target_groups.pop()

  def reset(camera):
    camera.pos = None
    camera.target_groups = []

  def update(camera):
    if not camera.pos or not camera.target_groups:
      return

    if camera.anim:
      start, goal = camera.anim.target
      camera.anim.update()
      camera.pos = vector.lerp(start, goal, camera.anim.pos)
      if camera.anim.done:
        camera.anim = None
      return

    target_pos = Camera.resolve_target_group(camera.target_groups[-1], camera.offset)
    target_vel = vector.scale(vector.subtract(target_pos, vector.subtract(camera.pos, camera.offset)), 1 / Camera.SPEED * 8)
    camera.vel = vector.scale(vector.subtract(target_vel, camera.vel), 1 / 8)
    camera.pos = vector.add(camera.pos, camera.vel, vector.negate(camera.offset))


    camera_x = camera.pos[0] - camera.offset[0]
    camera_y = camera.pos[1] - camera.offset[1]

    # constraints handling
    if camera.constraints and camera.size[0] >= camera.constraints.width:
      camera_x = camera.constraints.width / 2
      camera.pos = (camera_x, camera_y)

    elif camera.constraints:
      constraint_left = camera.constraints.left + camera.size[0] / 2
      if camera.pos[0] < constraint_left:
        camera.pos = (constraint_left, camera_y)

      constraint_right = camera.constraints.right - camera.size[0] / 2
      if camera.pos[0] > constraint_right:
        camera.pos = (constraint_right, camera_y)


    if camera.constraints and camera.size[1] >= camera.constraints.height:
      camera_y = camera.constraints.height / 2
      camera.pos = (camera_x, camera_y)

    elif camera.constraints:
      constraint_top = camera.constraints.top + camera.size[1] / 2
      if camera.pos[1] < constraint_top:
        camera.pos = (camera_x, constraint_top)

      constraint_bottom = camera.constraints.bottom - camera.size[1] / 2
      if camera.pos[1] > constraint_bottom:
        camera.pos = (camera_x, constraint_bottom)
