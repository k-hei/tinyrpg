from anims import Anim

class FrameAnim(Anim):
  def __init__(anim, frames=[], frame_duration=0, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if not anim.frames:
      anim.frames = frames
    if not anim.frame_duration:
      anim.frame_duration = frame_duration
    anim.frame_index = 0

  def frame(anim):
    return anim.frames[anim.frame_index] # separate for serialization

  def update(anim):
    time = super().update()
    if anim.done:
      return anim.frames[-1]
    if anim.time < 0:
      anim.frame = None
      return None
    frame_duration = anim.frame_duration or anim.duration / len(anim.frames)
    anim_duration = frame_duration * len(anim.frames)
    frame_index = int(time % anim_duration / anim_duration * len(anim.frames))
    anim.frame_index = frame_index
    return frame_index
