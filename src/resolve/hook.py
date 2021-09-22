from dungeon.hooks.arena.defeat import on_defeat as arenadefeat
from dungeon.hooks.arena.place import on_place as arenaplace
from dungeon.hooks.oasis.place import on_place as oasisplace
from dungeon.hooks.mageboss.focus import on_focus as magebossfocus
from dungeon.hooks.mageboss.enter import on_enter as magebossenter
from dungeon.hooks.mageboss.defeat import on_defeat as magebossdefeat

def resolve_hook(key):
  if key == "arena.defeat": return arenadefeat
  if key == "arena.place": return arenaplace
  if key == "oasis.place": return oasisplace
  if key == "mageboss.focus": return magebossfocus
  if key == "mageboss.enter": return magebossenter
  if key == "mageboss.defeat": return magebossdefeat
