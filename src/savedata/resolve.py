from items.ailment.antidote import Antidote
from items.ailment.amethyst import Amethyst
from items.sp.bread import Bread
from items.sp.cheese import Cheese
from items.sp.sapphire import Sapphire
from items.sp.fish import Fish
from items.materials.diamond import Diamond
from items.materials.angeltears import AngelTears
from items.materials.redferrule import RedFerrule
from items.hp.ankh import Ankh
from items.hp.ruby import Ruby
from items.hp.elixir import Elixir
from items.hp.potion import Potion
from items.dungeon.key import Key
from items.dungeon.emerald import Emerald
from items.dungeon.balloon import Balloon
from skills.ailment.virus import Virus
from skills.ailment.somnus import Somnus
from skills.ailment.exoculo import Exoculo
from skills.ailment.steal import Steal
from skills.weapon.rustyblade import RustyBlade
from skills.weapon.tackle import Tackle
from skills.weapon.stick import Stick
from skills.weapon.club import Club
from skills.weapon.rare import RareWeapon
from skills.weapon.cudgel import Cudgel
from skills.weapon.broadsword import BroadSword
from skills.weapon.longinus import Longinus
from skills.weapon.caladbolg import Caladbolg
from skills.weapon.mjolnir import Mjolnir
from skills.attack.shieldbash import ShieldBash
from skills.attack.helmsplitter import HelmSplitter
from skills.attack.cleave import Cleave
from skills.attack.blitzritter import Blitzritter
from skills.attack.rendinggale import RendingGale
from skills.magic.vortex import Vortex
from skills.magic.hirudo import Hirudo
from skills.magic.ignis import Ignis
from skills.magic.accerso import Accerso
from skills.magic.fulgur import Fulgur
from skills.magic.glacio import Glacio
from skills.magic.congelatio import Congelatio
from skills.field.detectmana import DetectMana
from skills.support.anastasis import Anastasis
from skills.support.counter import Counter
from skills.support.sana import Sana
from skills.armor.buckler import Buckler
from skills.armor.hpup import HpUp
from dungeon.props.bag import Bag
from dungeon.props.treasuredoor import TreasureDoor
from dungeon.props.palm import Palm
from dungeon.props.battledoor import BattleDoor
from dungeon.props.coffin import Coffin
from dungeon.props.soul import Soul
from dungeon.props.pushblock import PushBlock
from dungeon.props.arrowtrap import ArrowTrap
from dungeon.props.altar import Altar
from dungeon.props.door import Door
from dungeon.props.pushtile import PushTile
from dungeon.props.puzzledoor import PuzzleDoor
from dungeon.props.pillar import Pillar
from dungeon.props.chest import Chest
from dungeon.features.oasisroom import OasisRoom
from dungeon.features.emeraldroom import EmeraldRoom
from dungeon.features.guardroom import GuardRoom
from dungeon.features.traproom import TrapRoom
from dungeon.features.elevroom import ElevRoom
from dungeon.features.pitroom import PitRoom
from dungeon.features.genieroom import GenieRoom
from dungeon.features.altarroom import AltarRoom
from dungeon.features.coffinroom import CoffinRoom
from dungeon.features.hallroom import HallRoom
from dungeon.features.pushblockroom import PushBlockRoom
from dungeon.features.battleroom import BattleRoom
from dungeon.features.puzzleroom import PuzzleRoom
from dungeon.features.arenaroom import ArenaRoom
from dungeon.features.maze import Maze
from dungeon.features.magebossroom import MageBossRoom
from dungeon.features.raretreasureroom import RareTreasureRoom
from dungeon.features.itemroom import ItemRoom
from dungeon.features.vertroom import VerticalRoom
from dungeon.features.lockedexitroom import LockedExitRoom
from dungeon.features.specialroom import SpecialRoom
from dungeon.features.depthsroom import DepthsRoom
from dungeon.features.exitroom import ExitRoom
from dungeon.features.room import Room
from dungeon.features.enemyroom import EnemyRoom
from dungeon.actors.genie import Genie
from dungeon.actors.npc import Npc
from dungeon.actors.skeleton import Skeleton
from dungeon.actors.mage import Mage
from dungeon.actors.eye import Eyeball
from dungeon.actors.mimic import Mimic
from dungeon.actors.knight import Knight
from dungeon.actors.mushroom import Mushroom
from dungeon.actors.guard import GuardActor
from dungeon.actors.soldier import Soldier
from dungeon.floors.floor1 import Floor1
from dungeon.floors.floor3 import Floor3
from dungeon.floors.floor2 import Floor2

def resolve_item(key):
  if key == "Antidote": return Antidote
  if key == "Amethyst": return Amethyst
  if key == "Bread": return Bread
  if key == "Cheese": return Cheese
  if key == "Sapphire": return Sapphire
  if key == "Fish": return Fish
  if key == "Diamond": return Diamond
  if key == "AngelTears": return AngelTears
  if key == "RedFerrule": return RedFerrule
  if key == "Ankh": return Ankh
  if key == "Ruby": return Ruby
  if key == "Elixir": return Elixir
  if key == "Potion": return Potion
  if key == "Key": return Key
  if key == "Emerald": return Emerald
  if key == "Balloon": return Balloon

def resolve_skill(key):
  if key == "Virus": return Virus
  if key == "Somnus": return Somnus
  if key == "Exoculo": return Exoculo
  if key == "Steal": return Steal
  if key == "RustyBlade": return RustyBlade
  if key == "Tackle": return Tackle
  if key == "Stick": return Stick
  if key == "Club": return Club
  if key == "RareWeapon": return RareWeapon
  if key == "Cudgel": return Cudgel
  if key == "BroadSword": return BroadSword
  if key == "Longinus": return Longinus
  if key == "Caladbolg": return Caladbolg
  if key == "Mjolnir": return Mjolnir
  if key == "ShieldBash": return ShieldBash
  if key == "HelmSplitter": return HelmSplitter
  if key == "Cleave": return Cleave
  if key == "Blitzritter": return Blitzritter
  if key == "RendingGale": return RendingGale
  if key == "Vortex": return Vortex
  if key == "Hirudo": return Hirudo
  if key == "Ignis": return Ignis
  if key == "Accerso": return Accerso
  if key == "Fulgur": return Fulgur
  if key == "Glacio": return Glacio
  if key == "Congelatio": return Congelatio
  if key == "DetectMana": return DetectMana
  if key == "Anastasis": return Anastasis
  if key == "Counter": return Counter
  if key == "Sana": return Sana
  if key == "Buckler": return Buckler
  if key == "HpUp": return HpUp

def resolve_elem(key):
  if key == "Bag": return Bag
  if key == "TreasureDoor": return TreasureDoor
  if key == "Palm": return Palm
  if key == "BattleDoor": return BattleDoor
  if key == "Coffin": return Coffin
  if key == "Soul": return Soul
  if key == "PushBlock": return PushBlock
  if key == "ArrowTrap": return ArrowTrap
  if key == "Altar": return Altar
  if key == "Door": return Door
  if key == "PushTile": return PushTile
  if key == "PuzzleDoor": return PuzzleDoor
  if key == "Pillar": return Pillar
  if key == "Chest": return Chest
  if key == "OasisRoom": return OasisRoom
  if key == "EmeraldRoom": return EmeraldRoom
  if key == "GuardRoom": return GuardRoom
  if key == "TrapRoom": return TrapRoom
  if key == "ElevRoom": return ElevRoom
  if key == "PitRoom": return PitRoom
  if key == "GenieRoom": return GenieRoom
  if key == "AltarRoom": return AltarRoom
  if key == "CoffinRoom": return CoffinRoom
  if key == "HallRoom": return HallRoom
  if key == "PushBlockRoom": return PushBlockRoom
  if key == "BattleRoom": return BattleRoom
  if key == "PuzzleRoom": return PuzzleRoom
  if key == "ArenaRoom": return ArenaRoom
  if key == "Maze": return Maze
  if key == "MageBossRoom": return MageBossRoom
  if key == "RareTreasureRoom": return RareTreasureRoom
  if key == "ItemRoom": return ItemRoom
  if key == "VerticalRoom": return VerticalRoom
  if key == "LockedExitRoom": return LockedExitRoom
  if key == "SpecialRoom": return SpecialRoom
  if key == "DepthsRoom": return DepthsRoom
  if key == "ExitRoom": return ExitRoom
  if key == "Room": return Room
  if key == "EnemyRoom": return EnemyRoom
  if key == "Genie": return Genie
  if key == "Npc": return Npc
  if key == "Skeleton": return Skeleton
  if key == "Mage": return Mage
  if key == "Eyeball": return Eyeball
  if key == "Mimic": return Mimic
  if key == "Knight": return Knight
  if key == "Mushroom": return Mushroom
  if key == "GuardActor": return GuardActor
  if key == "Soldier": return Soldier
  if key == "Floor1": return Floor1
  if key == "Floor3": return Floor3
  if key == "Floor2": return Floor2

def resolve_material(material):
  if material is Diamond: return None
  if material is AngelTears: return Eyeball
  if material is RedFerrule: return Mushroom
  if material is Club: return Skeleton
  if material is BroadSword: return Mage
