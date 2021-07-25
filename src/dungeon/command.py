from dataclasses import dataclass
from types import FunctionType as function
from dungeon.actors import DungeonActor
from skills import Skill

@dataclass
class Command:
  on_end: function = None

@dataclass
class MoveCommand(Command):
  direction: tuple[int, int] = None

@dataclass
class MoveToCommand(Command):
  dest: tuple[int, int] = None

@dataclass
class PushCommand(Command):
  target: DungeonActor = None

@dataclass
class SkillCommand(Command):
  skill: Skill = None
  dest: tuple[int, int] = None
