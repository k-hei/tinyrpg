from dungeon.hooks.oasis.place import on_place as oasisplace
from dungeon.hooks.mageboss.focus import on_focus as magebossfocus

def resolve_hook(key):
  if key == "oasis.place": return oasisplace
  if key == "mageboss.focus": return magebossfocus
