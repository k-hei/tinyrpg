from items.ailment.amethyst import Amethyst
from items.ailment.antidote import Antidote
from items.dungeon.balloon import Balloon
from items.dungeon.emerald import Emerald
from items.dungeon.key import Key
from items.hp.ankh import Ankh
from items.hp.elixir import Elixir
from items.hp.potion import Potion
from items.hp.ruby import Ruby
from items.materials.angeltears import AngelTears
from items.materials.diamond import Diamond
from items.materials.redferrule import RedFerrule
from items.sp.bread import Bread
from items.sp.cheese import Cheese
from items.sp.fish import Fish
from items.sp.sapphire import Sapphire
from skills.ailment.exoculo import Exoculo
from skills.ailment.somnus import Somnus
from skills.ailment.steal import Steal
from skills.ailment.virus import Virus
from skills.armor.hpup import HpUp
from skills.attack.blitzritter import Blitzritter
from skills.attack.cleave import Cleave
from skills.attack.helmsplitter import HelmSplitter
from skills.attack.rendinggale import RendingGale
from skills.attack.shieldbash import ShieldBash
from skills.field.detectmana import DetectMana
from skills.magic.accerso import Accerso
from skills.magic.congelatio import Congelatio
from skills.magic.fulgur import Fulgur
from skills.magic.glacio import Glacio
from skills.magic.hirudo import Hirudo
from skills.magic.ignis import Ignis
from skills.magic.vortex import Vortex
from skills.support.anastasis import Anastasis
from skills.support.counter import Counter
from skills.support.sana import Sana
from skills.weapon.broadsword import BroadSword
from skills.weapon.caladbolg import Caladbolg
from skills.weapon.club import Club
from skills.weapon.longinus import Longinus
from skills.weapon.mjolnir import Mjolnir
from skills.weapon.rare import RareWeapon
from skills.weapon.rustyblade import RustyBlade
from skills.weapon.stick import Stick
from skills.weapon.tackle import Tackle
from dungeon.actors.eye import Eye
from dungeon.actors.genie import Genie
from dungeon.actors.guard import GuardActor
from dungeon.actors.knight import Knight
from dungeon.actors.mage import Mage
from dungeon.actors.mimic import Mimic
from dungeon.actors.mushroom import Mushroom
from dungeon.actors.npc import Npc
from dungeon.actors.skeleton import Skeleton
from dungeon.actors.soldier import Soldier
from dungeon.features.altarroom import AltarRoom
from dungeon.features.arenaroom import ArenaRoom
from dungeon.features.battleroom import BattleRoom
from dungeon.features.coffinroom import CoffinRoom
from dungeon.features.depthsroom import DepthsRoom
from dungeon.features.elevroom import ElevRoom
from dungeon.features.emeraldroom import EmeraldRoom
from dungeon.features.enemyroom import EnemyRoom
from dungeon.features.exitroom import ExitRoom
from dungeon.features.genieroom import GenieRoom
from dungeon.features.guardroom import GuardRoom
from dungeon.features.hallroom import HallRoom
from dungeon.features.itemroom import ItemRoom
from dungeon.features.lockedexitroom import LockedExitRoom
from dungeon.features.magebossroom import MageBossRoom
from dungeon.features.maze import Maze
from dungeon.features.oasisroom import OasisRoom
from dungeon.features.pitroom import PitRoom
from dungeon.features.raretreasureroom import RareTreasureRoom
from dungeon.features.room import Room
from dungeon.features.specialroom import SpecialRoom
from dungeon.features.vertroom import VerticalRoom
from dungeon.props.altar import Altar
from dungeon.props.bag import Bag
from dungeon.props.battledoor import BattleDoor
from dungeon.props.chest import Chest
from dungeon.props.coffin import Coffin
from dungeon.props.door import Door
from dungeon.props.palm import Palm
from dungeon.props.pillar import Pillar
from dungeon.props.pushblock import PushBlock
from dungeon.props.pushtile import PushTile
from dungeon.props.puzzledoor import PuzzleDoor
from dungeon.props.soul import Soul
from dungeon.props.treasuredoor import TreasureDoor

def resolve_item(key):
  if key == "Amethyst": return Amethyst
  if key == "Antidote": return Antidote
  if key == "Balloon": return Balloon
  if key == "Emerald": return Emerald
  if key == "Key": return Key
  if key == "Ankh": return Ankh
  if key == "Elixir": return Elixir
  if key == "Potion": return Potion
  if key == "Ruby": return Ruby
  if key == "AngelTears": return AngelTears
  if key == "Diamond": return Diamond
  if key == "RedFerrule": return RedFerrule
  if key == "Bread": return Bread
  if key == "Cheese": return Cheese
  if key == "Fish": return Fish
  if key == "Sapphire": return Sapphire

def resolve_skill(key):
  if key == "Exoculo": return Exoculo
  if key == "Somnus": return Somnus
  if key == "Steal": return Steal
  if key == "Virus": return Virus
  if key == "HpUp": return HpUp
  if key == "Blitzritter": return Blitzritter
  if key == "Cleave": return Cleave
  if key == "HelmSplitter": return HelmSplitter
  if key == "RendingGale": return RendingGale
  if key == "ShieldBash": return ShieldBash
  if key == "DetectMana": return DetectMana
  if key == "Accerso": return Accerso
  if key == "Congelatio": return Congelatio
  if key == "Fulgur": return Fulgur
  if key == "Glacio": return Glacio
  if key == "Hirudo": return Hirudo
  if key == "Ignis": return Ignis
  if key == "Vortex": return Vortex
  if key == "Anastasis": return Anastasis
  if key == "Counter": return Counter
  if key == "Sana": return Sana
  if key == "BroadSword": return BroadSword
  if key == "Caladbolg": return Caladbolg
  if key == "Club": return Club
  if key == "Longinus": return Longinus
  if key == "Mjolnir": return Mjolnir
  if key == "RareWeapon": return RareWeapon
  if key == "RustyBlade": return RustyBlade
  if key == "Stick": return Stick
  if key == "Tackle": return Tackle

def resolve_elem(key):
  if key == "Eye": return Eye
  if key == "Genie": return Genie
  if key == "GuardActor": return GuardActor
  if key == "Knight": return Knight
  if key == "Mage": return Mage
  if key == "Mimic": return Mimic
  if key == "Mushroom": return Mushroom
  if key == "Npc": return Npc
  if key == "Skeleton": return Skeleton
  if key == "Soldier": return Soldier
  if key == "AltarRoom": return AltarRoom
  if key == "ArenaRoom": return ArenaRoom
  if key == "BattleRoom": return BattleRoom
  if key == "CoffinRoom": return CoffinRoom
  if key == "DepthsRoom": return DepthsRoom
  if key == "ElevRoom": return ElevRoom
  if key == "EmeraldRoom": return EmeraldRoom
  if key == "EnemyRoom": return EnemyRoom
  if key == "ExitRoom": return ExitRoom
  if key == "GenieRoom": return GenieRoom
  if key == "GuardRoom": return GuardRoom
  if key == "HallRoom": return HallRoom
  if key == "ItemRoom": return ItemRoom
  if key == "LockedExitRoom": return LockedExitRoom
  if key == "MageBossRoom": return MageBossRoom
  if key == "Maze": return Maze
  if key == "OasisRoom": return OasisRoom
  if key == "PitRoom": return PitRoom
  if key == "RareTreasureRoom": return RareTreasureRoom
  if key == "Room": return Room
  if key == "SpecialRoom": return SpecialRoom
  if key == "VerticalRoom": return VerticalRoom
  if key == "Altar": return Altar
  if key == "Bag": return Bag
  if key == "BattleDoor": return BattleDoor
  if key == "Chest": return Chest
  if key == "Coffin": return Coffin
  if key == "Door": return Door
  if key == "Palm": return Palm
  if key == "Pillar": return Pillar
  if key == "PushBlock": return PushBlock
  if key == "PushTile": return PushTile
  if key == "PuzzleDoor": return PuzzleDoor
  if key == "Soul": return Soul
  if key == "TreasureDoor": return TreasureDoor

def resolve_material(material):
  if material is AngelTears: return Eye
  if material is Diamond: return None
  if material is RedFerrule: return Mushroom
  if material is BroadSword: return Mage
