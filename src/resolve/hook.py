from dungeon.hooks.emerald.enter import on_enter as emeraldenter
from dungeon.hooks.arena.enter import on_enter as arenaenter
from dungeon.hooks.arena.defeat import on_defeat as arenadefeat
from dungeon.hooks.arena.place import on_place as arenaplace
from dungeon.hooks.coffin.enter import on_enter as coffinenter
from dungeon.hooks.coffin.defeat import on_defeat as coffindefeat
from dungeon.hooks.shrine.focus import on_enter as shrinefocus
from dungeon.hooks.shrine.magespin import sequence_mage_spin as shrinemagespin
from dungeon.hooks.shrine.walk import on_walk as shrinewalk
from dungeon.hooks.shrine.magebump import sequence_mage_bump as shrinemagebump
from dungeon.hooks.shrine.magestruggle import sequence_mage_struggle as shrinemagestruggle
from dungeon.hooks.shrine.collapse import on_collapse as shrinecollapse
from dungeon.hooks.trapbase.place import on_place as trapbaseplace
from dungeon.hooks.entry2f.focus import on_focus as entry2ffocus
from dungeon.hooks.oasis.place import on_place as oasisplace
from dungeon.hooks.mageboss.focus import on_focus as magebossfocus
from dungeon.hooks.mageboss.enter import on_enter as magebossenter
from dungeon.hooks.mageboss.defeat import on_defeat as magebossdefeat

def resolve_hook(key):
  if key == "emerald.enter": return emeraldenter
  if key == "arena.enter": return arenaenter
  if key == "arena.defeat": return arenadefeat
  if key == "arena.place": return arenaplace
  if key == "coffin.enter": return coffinenter
  if key == "coffin.defeat": return coffindefeat
  if key == "shrine.focus": return shrinefocus
  if key == "shrine.magespin": return shrinemagespin
  if key == "shrine.walk": return shrinewalk
  if key == "shrine.magebump": return shrinemagebump
  if key == "shrine.magestruggle": return shrinemagestruggle
  if key == "shrine.collapse": return shrinecollapse
  if key == "trapbase.place": return trapbaseplace
  if key == "entry2f.focus": return entry2ffocus
  if key == "oasis.place": return oasisplace
  if key == "mageboss.focus": return magebossfocus
  if key == "mageboss.enter": return magebossenter
  if key == "mageboss.defeat": return magebossdefeat
