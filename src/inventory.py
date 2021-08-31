from items.materials import MaterialItem
from config import INVENTORY_COLS, INVENTORY_ROWS

class Inventory:
  tabs = ["consumables", "materials", "equipment"]

  def tab(item):
    if type(item) is type and issubclass(item, MaterialItem):
      return "materials"
    else:
      return "consumables"

  def filter(items, tab):
    return [item for item in items if Inventory.tab(item) == tab]

  def is_full(items, tab):
    return len(Inventory.filter(items, tab)) >= INVENTORY_COLS * INVENTORY_ROWS

  def append(items, item):
    if Inventory.is_full(items, Inventory.tab(item)):
      return False
    items.append(item)
    return True
