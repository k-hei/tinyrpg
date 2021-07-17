from anims import Anim

class FrameAnim(Anim):
  frames = []
  frame_duration = 0

  def __init__(anim, frames=[], frame_duration=0, *args, **kwargs):
    super().__init__(*args, **kwargs)
    anim.frames = anim.frames or frames
    anim.frame_duration = anim.frame_duration or frame_duration
    anim.frame_index = 0

  def frame(anim): # method instead of prop for serialization
    return anim.frames[anim.frame_index] if anim.frame_index is not None else None

  def update(anim):
    time = super().update()
    if anim.done:
      return anim.frames[-1]
    if anim.time < 0:
      anim.frame_index = None
      return None
    frame_duration = anim.frame_duration or anim.duration / len(anim.frames)
    anim_duration = frame_duration * len(anim.frames)
    frame_index = int(time % anim_duration / anim_duration * len(anim.frames))
    anim.frame_index = frame_index
    return frame_index
