class Component:
  def __init__(comp):
    comp.active = True
    comp.done = False

  def enter(comp):
    comp.active = True

  def exit(comp):
    comp.active = False
