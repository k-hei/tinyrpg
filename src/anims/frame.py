from anims import Anim

class FrameAnim(Anim):
  def __init__(anim, frames, frame_duration=0, *args, **kwargs):
    super().__init__(*args, **kwargs)
    anim.frames = frames
    anim.frame = frames[0]
    anim.frame_duration = frame_duration

  def update(anim):
    time = super().update()
    if anim.done:
      return anim.frames[-1]
    frame_duration = anim.frame_duration or anim.duration / len(anim.frames)
    anim_duration = frame_duration * len(anim.frames)
    frame_index = int(anim.time % anim_duration / anim_duration * len(anim.frames))
    frame = anim.frames[frame_index]
    anim.frame = frame
    return frame
