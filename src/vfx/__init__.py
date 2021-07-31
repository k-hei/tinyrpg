from colors.palette import BLACK

class Vfx:
  def __init__(vfx, pos, kind=None, anim=None, color=BLACK, vel=(0, 0)):
    vfx.kind = kind
    vfx.pos = pos
    vfx.anim = anim
    vfx.color = color
    vfx.vel = vel
    vfx.done = False

  def update(vfx, *_):
    if vfx.done:
      return None
    pos_x, pos_y = vfx.pos
    vel_x, vel_y = vfx.vel
    vfx.pos = (pos_x + vel_x, pos_y + vel_y)
    if vfx.anim:
      if vfx.anim.done:
        vfx.done = True
      else:
        vfx.anim.update()
      return vfx.anim.frame()
