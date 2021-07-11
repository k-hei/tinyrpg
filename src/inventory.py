from items.materials import MaterialItem

class Inventory:
  tabs = ["consumables", "materials", "equipment"]

  def tab(item):
    if issubclass(item, MaterialItem):
      return "materials"
    else:
      return "consumables"

  def __init__(inv, size, items=[]):
    cols, rows = size
    inv.cols = cols
    inv.rows = rows
    inv.items = items

  def filter(inv, tab):
    return [item for item in inv.items if Inventory.tab(item) == tab]

  def is_full(inv, tab):
    return len(inv.filter(tab)) >= inv.cols * inv.rows

  def append(inv, item):
    if not inv.is_full(Inventory.tab(item)):
      inv.items.append(item)
      return True
    else:
      return False
