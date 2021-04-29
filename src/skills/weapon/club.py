from dataclasses import dataclass
from skills.weapon import WeaponSkill
from cores import Core
from cores.knight import Knight
from assets import load as use_assets

@dataclass
class Club(WeaponSkill):
  name: str = "Club"
  desc: str = "A makeshift weapon."
  element: str = "axe"
  st: int = 2
  users: tuple[Core] = (Knight,)
  blocks: tuple[tuple[int, int]] = (
    (0, 0),
    (1, 0),
  )
