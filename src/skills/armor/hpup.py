from dataclasses import dataclass
from skills import Skill
from cores import Core
from cores.knight import Knight
from cores.mage import Mage

@dataclass
class HpUp(Skill):
  hp: int = 5
  name: str = "HP +5"
  desc: str = "Increases HP by 5"
  users: tuple[Core] = (Knight, Mage)
