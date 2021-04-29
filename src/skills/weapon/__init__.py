from dataclasses import dataclass
from skills import Skill
from palette import GRAY

@dataclass
class WeaponSkill(Skill):
  kind: str = "weapon"
  cost: int = 1
  st: int = 0
  color: tuple = GRAY
