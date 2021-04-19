from element import Element

class Prop(Element):
  def __init__(prop, name=None, solid=True):
    super().__init__(name)
    prop.solid = solid

  def effect(prop):
    pass
