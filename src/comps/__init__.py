class Component:
  def __init__(comp, pos=(0, 0)):
    comp.pos = pos
    comp.active = True
    comp.exiting = False
    comp.anims = []
    comp.done = False

  def enter(comp):
    comp.active = True
    comp.exiting = False

  def exit(comp):
    comp.active = False
    comp.exiting = True
