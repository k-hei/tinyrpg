class Actor:
  def __init__(actor, kind, cell):
    actor.kind = kind
    actor.cell = cell
    actor.facing = (1, 0)
    actor.visible_cells = []

  def move(actor, delta, stage):
    pass
