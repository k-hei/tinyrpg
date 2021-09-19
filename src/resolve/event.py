from dungeon.events.oasis.place import on_place as oasisplace
from dungeon.events.mageboss.focus import on_focus as magebossfocus

def resolve_event(key):
  if key == "oasis.place": return oasisplace
  if key == "mageboss.focus": return magebossfocus
