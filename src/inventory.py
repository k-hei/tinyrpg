class Inventory:
  def __init__(inv, cols, rows):
    inv.cols = cols
    inv.rows = rows
    inv.items = []

  def is_full(inv):
    return len(inv.items) == inv.cols * inv.rows

  def append(inv, item):
    if not inv.is_full():
      inv.items.append(item)
      return True
    else:
      return False
