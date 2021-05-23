from anims import Anim

class FrameAnim(Anim):
  def __init__(anim, duration, frames, delay=0, target=None, on_start=None, on_end=None):
    super().__init__(duration, delay, target, on_start, on_end)
    anim.frames = frames
    anim.frame = frames[0]

  def update(anim):
    time = super().update()
    if anim.done:
      return anim.frames[-1]
    t = anim.time / anim.duration
    frame_duration = anim.duration / len(anim.frames)
    frame_index = int(anim.time / frame_duration)
    frame = anim.frames[frame_index]
    anim.frame = frame
    return frame
