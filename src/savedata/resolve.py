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
from dungeon.props.poisonpuff import PoisonPuff
from dungeon.props.coffin import Coffin
from dungeon.props.vcoffin import VCoffin
from dungeon.props.vase import Vase
from dungeon.props.soul import Soul
from dungeon.props.pushblock import PushBlock
from dungeon.props.arrowtrap import ArrowTrap
from dungeon.props.altar import Altar
from dungeon.props.door import Door
from dungeon.props.pushtile import PushTile
from dungeon.props.itemdrop import ItemDrop
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
from dungeon.features.gauntletroom import GauntletRoom
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
from dungeon.actors.mummy import Mummy
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
from dungeon.floors.debugfloor import DebugFloor
from dungeon.floors.floor1 import Floor1
from dungeon.floors.genericfloor import GenericFloor
from dungeon.floors.floor3 import Floor3
from dungeon.floors.floor2 import Floor2
from items.ailment.booze import Booze as BoozeItem
from items.ailment.topaz import Topaz as TopazItem
from items.ailment.musicbox import MusicBox as MusicBoxItem
from items.ailment.antidote import Antidote as AntidoteItem
from items.ailment.amethyst import Amethyst as AmethystItem
from items.ailment.lovepotion import LovePotion as LovePotionItem
from items.sp.bread import Bread as BreadItem
from items.sp.berry import Berry as BerryItem
from items.sp.cheese import Cheese as CheeseItem
from items.sp.sapphire import Sapphire as SapphireItem
from items.sp.fish import Fish as FishItem
from items.materials.diamond import Diamond as DiamondItem
from items.materials.beetle import Beetle as BeetleItem
from items.materials.angeltears import AngelTears as AngelTearsItem
from items.materials.crownjewel import CrownJewel as CrownJewelItem
from items.materials.redferrule import RedFerrule as RedFerruleItem
from items.hp.ankh import Ankh as AnkhItem
from items.hp.ruby import Ruby as RubyItem
from items.hp.elixir import Elixir as ElixirItem
from items.hp.potion import Potion as PotionItem
from items.dungeon.key import Key as KeyItem
from items.dungeon.emerald import Emerald as EmeraldItem
from items.dungeon.balloon import Balloon as BalloonItem
from cores.genie import Genie as GenieCore
from cores.rogue import Rogue as RogueCore
from cores.beetle import Beetle as BeetleCore
from cores.mage import Mage as MageCore
from cores.husband import Husband as HusbandCore
from cores.wife import Wife as WifeCore
from cores.knight import Knight as KnightCore
from cores.radhead import Radhead as RadheadCore
from cores.beetless import Beetless as BeetlessCore
from cores.ghost import Ghost as GhostCore
from cores.rat import Rat as RatCore

def resolve_item(key):
  if key == "Booze": return BoozeItem
  if key == "Topaz": return TopazItem
  if key == "MusicBox": return MusicBoxItem
  if key == "Antidote": return AntidoteItem
  if key == "Amethyst": return AmethystItem
  if key == "LovePotion": return LovePotionItem
  if key == "Bread": return BreadItem
  if key == "Berry": return BerryItem
  if key == "Cheese": return CheeseItem
  if key == "Sapphire": return SapphireItem
  if key == "Fish": return FishItem
  if key == "Diamond": return DiamondItem
  if key == "Beetle": return BeetleItem
  if key == "AngelTears": return AngelTearsItem
  if key == "CrownJewel": return CrownJewelItem
  if key == "RedFerrule": return RedFerruleItem
  if key == "Ankh": return AnkhItem
  if key == "Ruby": return RubyItem
  if key == "Elixir": return ElixirItem
  if key == "Potion": return PotionItem
  if key == "Key": return KeyItem
  if key == "Emerald": return EmeraldItem
  if key == "Balloon": return BalloonItem

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

def resolve_core(key):
  if key == "Genie": return GenieCore
  if key == "Rogue": return RogueCore
  if key == "Beetle": return BeetleCore
  if key == "Mage": return MageCore
  if key == "Husband": return HusbandCore
  if key == "Wife": return WifeCore
  if key == "Knight": return KnightCore
  if key == "Radhead": return RadheadCore
  if key == "Beetless": return BeetlessCore
  if key == "Ghost": return GhostCore
  if key == "Rat": return RatCore

def resolve_elem(key):
  if key == "Bag": return Bag
  if key == "TreasureDoor": return TreasureDoor
  if key == "Palm": return Palm
  if key == "BattleDoor": return BattleDoor
  if key == "PoisonPuff": return PoisonPuff
  if key == "Coffin": return Coffin
  if key == "VCoffin": return VCoffin
  if key == "Vase": return Vase
  if key == "Soul": return Soul
  if key == "PushBlock": return PushBlock
  if key == "ArrowTrap": return ArrowTrap
  if key == "Altar": return Altar
  if key == "Door": return Door
  if key == "PushTile": return PushTile
  if key == "ItemDrop": return ItemDrop
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
  if key == "GauntletRoom": return GauntletRoom
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
  if key == "Mummy": return Mummy
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
  if key == "DebugFloor": return DebugFloor
  if key == "Floor1": return Floor1
  if key == "GenericFloor": return GenericFloor
  if key == "Floor3": return Floor3
  if key == "Floor2": return Floor2

def resolve_material(material):
  if material is Diamond: return None
  if material is Beetle: return None
  if material is AngelTears: return Eyeball
  if material is CrownJewel: return Mummy
  if material is RedFerrule: return Mushroom
  if material is Club: return Skeleton
  if material is BroadSword: return Mage
