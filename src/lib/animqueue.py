class AnimQueue:
  def __init__(queue):
    queue.anims = []

  def play_anims(queue, anims):
    not queue.anims and queue.anims.append([])
    queue.anims[0].extend(anims)

  def play_anim(queue, anim):
    queue.play_anims([anim])

  def queue_anims(queue, anims):
    queue.anims.append(anims)

  def queue_anim(queue, anim):
    queue.queue_anims([anim])

  def update(queue):
    queue.anims = [
      [(a.update(), a)[-1] for a in g if not a.done]
        for g in queue.anims
    ]
