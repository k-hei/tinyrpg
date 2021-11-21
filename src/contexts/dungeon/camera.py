from pygame import Rect
import lib.vector as vector

class Camera:
  SPEED = 8

  def resolve_target(target):
    if type(target) is tuple:
      return target

    if type(target) is Rect:
      return target.center

    return target.pos

  def __init__(camera, size):
    camera.size = size
    camera.pos = None
    camera.vel = (0, 0)
    camera.target = None

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

  def focus(camera, target):
    if camera.target == target or camera.target is target:
      return

    if target is None:
      camera.blur()
      return

    camera.target = target
    if not camera.pos:
      camera.pos = Camera.resolve_target(target)

  def blur(camera):
    camera.target = None

  def update(camera):
    if not camera.pos:
      return
    target_pos = Camera.resolve_target(camera.target)
    target_vel = vector.scale(vector.subtract(target_pos, camera.pos), 1 / Camera.SPEED * 8)
    camera.vel = vector.scale(vector.subtract(target_vel, camera.vel), 1 / 8)
    camera.pos = vector.add(camera.pos, camera.vel)
