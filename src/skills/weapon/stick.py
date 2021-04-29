from dataclasses import dataclass
from skills.weapon import WeaponSkill
from cores.knight import Knight

@dataclass
class Stick(WeaponSkill):
  name: str = "Stick"
  desc: str = "A makeshift weapon"
  element: str = "lance"
  cost: int = 1
  st: int = 2
  users: tuple = (Knight,)
  blocks: tuple = (
    (0, 0),
    (1, 0)
  )
