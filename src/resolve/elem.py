from dungeon.props.bag import Bag
from dungeon.props.treasuredoor import TreasureDoor
from dungeon.props.palm import Palm
from dungeon.props.battledoor import BattleDoor
from dungeon.props.secretdoor import SecretDoor
from dungeon.props.poisonpuff import PoisonPuff
from dungeon.props.coffin import Coffin
from dungeon.props.vcoffin import VCoffin
from dungeon.props.vase import Vase
from dungeon.props.soul import Soul
from dungeon.props.pushblock import PushBlock
from dungeon.props.arrowtrap import ArrowTrap
from dungeon.props.altar import Altar
from dungeon.props.trap import Trap
from dungeon.props.rarechest import RareChest
from dungeon.props.door import Door
from dungeon.props.pushtile import PushTile
from dungeon.props.itemdrop import ItemDrop
from dungeon.props.table import Table
from dungeon.props.puzzledoor import PuzzleDoor
from dungeon.props.pillar import Pillar
from dungeon.props.column import Column
from dungeon.props.raretreasuredoor import RareTreasureDoor
from dungeon.props.chest import Chest
from dungeon.status.defense import DefEffect
from dungeon.status.attack import AtkEffect
from dungeon.actors.genie import Genie
from dungeon.actors.mummy import Mummy
from dungeon.actors.mageclone import MageClone
from dungeon.actors.npc import Npc
from dungeon.actors.skeleton import Skeleton
from dungeon.actors.eyeball import Eyeball
from dungeon.actors.beetle import Beetle
from dungeon.actors.mage import Mage
from dungeon.actors.mimic import Mimic
from dungeon.actors.knight import Knight
from dungeon.actors.mushroom import Mushroom
from dungeon.actors.guard import GuardActor
from dungeon.actors.ghost import Ghost
from locations.prejungle.elems.tree import PrejungleTree
from locations.prejungle.elems.bug import PrejungleBug
from locations.prejungle.elems.bush import PrejungleBush
from locations.prejungle.elems.berrytree import PrejungleBerryTree
from locations.prejungle.elems.grass import PrejungleGrass
from locations.prejungle.elems.redtree import PrejungleRedTree
from locations.prejungle.elems.rock import PrejungleRockXL
from locations.prejungle.elems.mosquito import PrejungleMosquito
from locations.desert.elems.roko import Roko
from locations.desert.elems.snake import DesertSnake
from locations.desert.elems.bush import DesertBush
from locations.desert.elems.cactus import DesertEvilCactus

def resolve_elem(key):
  if key == "Bag": return Bag
  if key == "TreasureDoor": return TreasureDoor
  if key == "Palm": return Palm
  if key == "BattleDoor": return BattleDoor
  if key == "SecretDoor": return SecretDoor
  if key == "PoisonPuff": return PoisonPuff
  if key == "Coffin": return Coffin
  if key == "VCoffin": return VCoffin
  if key == "Vase": return Vase
  if key == "Soul": return Soul
  if key == "PushBlock": return PushBlock
  if key == "ArrowTrap": return ArrowTrap
  if key == "Altar": return Altar
  if key == "Trap": return Trap
  if key == "RareChest": return RareChest
  if key == "Door": return Door
  if key == "PushTile": return PushTile
  if key == "ItemDrop": return ItemDrop
  if key == "Table": return Table
  if key == "PuzzleDoor": return PuzzleDoor
  if key == "Pillar": return Pillar
  if key == "Column": return Column
  if key == "RareTreasureDoor": return RareTreasureDoor
  if key == "Chest": return Chest
  if key == "DefEffect": return DefEffect
  if key == "AtkEffect": return AtkEffect
  if key == "Genie": return Genie
  if key == "Mummy": return Mummy
  if key == "MageClone": return MageClone
  if key == "Npc": return Npc
  if key == "Skeleton": return Skeleton
  if key == "Eyeball": return Eyeball
  if key == "Beetle": return Beetle
  if key == "Mage": return Mage
  if key == "Mimic": return Mimic
  if key == "Knight": return Knight
  if key == "Mushroom": return Mushroom
  if key == "GuardActor": return GuardActor
  if key == "Ghost": return Ghost
  if key == "PrejungleTree": return PrejungleTree
  if key == "PrejungleBug": return PrejungleBug
  if key == "PrejungleBush": return PrejungleBush
  if key == "PrejungleBerryTree": return PrejungleBerryTree
  if key == "PrejungleGrass": return PrejungleGrass
  if key == "PrejungleRedTree": return PrejungleRedTree
  if key == "PrejungleRockXL": return PrejungleRockXL
  if key == "PrejungleMosquito": return PrejungleMosquito
  if key == "Roko": return Roko
  if key == "DesertSnake": return DesertSnake
  if key == "DesertBush": return DesertBush
  if key == "DesertEvilCactus": return DesertEvilCactus
