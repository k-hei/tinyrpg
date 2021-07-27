from anims import Anim

class FrameAnim(Anim):
  frames = []
  frames_duration = 0

  def __init__(anim, frames=[], frames_duration=0, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if not anim.frames:
      anim.frames = frames
    if not anim.frames_duration:
      anim.frames_duration = frames_duration
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
    if type(anim.frames_duration) is list:
      frame_index = 0
      for duration in anim.frames_duration:
        if time < duration:
          break
        elif frame_index < len(anim.frames) - 1:
          time -= duration
          frame_index += 1
        else:
          anim.end()
          return anim.frames[-1]
    else:
      frame_duration = anim.frames_duration or anim.duration / len(anim.frames)
      anim_duration = frame_duration * len(anim.frames)
      frame_index = int(time % anim_duration / anim_duration * len(anim.frames))
    anim.frame_index = frame_index
    return frame_index
