from dungeon.actors.beetle import Beetle
from dungeon.actors.eyeball import Eyeball
from dungeon.actors.genie import Genie
from dungeon.actors.ghost import Ghost
from dungeon.actors.guard import GuardActor
from dungeon.actors.knight import Knight
from dungeon.actors.mage import Mage
from dungeon.actors.mimic import Mimic
from dungeon.actors.mummy import Mummy
from dungeon.actors.mushroom import Mushroom
from dungeon.actors.npc import Npc
from dungeon.actors.skeleton import Skeleton
from dungeon.props.altar import Altar
from dungeon.props.arrowtrap import ArrowTrap
from dungeon.props.bag import Bag
from dungeon.props.battledoor import BattleDoor
from dungeon.props.chest import Chest
from dungeon.props.coffin import Coffin
from dungeon.props.column import Column
from dungeon.props.door import Door
from dungeon.props.itemdrop import ItemDrop
from dungeon.props.palm import Palm
from dungeon.props.pillar import Pillar
from dungeon.props.poisonpuff import PoisonPuff
from dungeon.props.pushblock import PushBlock
from dungeon.props.pushtile import PushTile
from dungeon.props.puzzledoor import PuzzleDoor
from dungeon.props.rarechest import RareChest
from dungeon.props.raretreasuredoor import RareTreasureDoor
from dungeon.props.secretdoor import SecretDoor
from dungeon.props.soul import Soul
from dungeon.props.table import Table
from dungeon.props.treasuredoor import TreasureDoor
from dungeon.props.vase import Vase
from dungeon.props.vcoffin import VCoffin

def resolve_elem(key):
  if key == "Beetle": return Beetle
  if key == "Eyeball": return Eyeball
  if key == "Genie": return Genie
  if key == "Ghost": return Ghost
  if key == "GuardActor": return GuardActor
  if key == "Knight": return Knight
  if key == "Mage": return Mage
  if key == "Mimic": return Mimic
  if key == "Mummy": return Mummy
  if key == "Mushroom": return Mushroom
  if key == "Npc": return Npc
  if key == "Skeleton": return Skeleton
  if key == "Altar": return Altar
  if key == "ArrowTrap": return ArrowTrap
  if key == "Bag": return Bag
  if key == "BattleDoor": return BattleDoor
  if key == "Chest": return Chest
  if key == "Coffin": return Coffin
  if key == "Column": return Column
  if key == "Door": return Door
  if key == "ItemDrop": return ItemDrop
  if key == "Palm": return Palm
  if key == "Pillar": return Pillar
  if key == "PoisonPuff": return PoisonPuff
  if key == "PushBlock": return PushBlock
  if key == "PushTile": return PushTile
  if key == "PuzzleDoor": return PuzzleDoor
  if key == "RareChest": return RareChest
  if key == "RareTreasureDoor": return RareTreasureDoor
  if key == "SecretDoor": return SecretDoor
  if key == "Soul": return Soul
  if key == "Table": return Table
  if key == "TreasureDoor": return TreasureDoor
  if key == "Vase": return Vase
  if key == "VCoffin": return VCoffin
