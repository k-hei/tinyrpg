def step_anims(anims):
  return [(a.update(), a)[-1] for a in anims if not a.done]
