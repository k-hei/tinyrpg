from dungeon.events.oasisplace import on_place as oasisplace
from dungeon.events.magebossfocus import on_focus as magebossfocus

def resolve_event(key):
  if key == "oasisplace": return oasisplace
  if key == "magebossfocus": return magebossfocus
