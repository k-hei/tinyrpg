class Component:
  def __init__(comp):
    comp.active = True
    comp.exiting = False
    comp.done = False

  def enter(comp):
    comp.active = True
    comp.exiting = False

  def exit(comp):
    comp.active = False
    comp.exiting = True
