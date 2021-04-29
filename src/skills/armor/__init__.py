from dataclasses import dataclass
from skills import Skill

@dataclass
class ArmorSkill(Skill):
  hp: int = 0
