from dataclasses import dataclass
from skills.weapon import WeaponSkill
from cores import Core
from cores.knight import Knight
from assets import load as use_assets
from palette import PINK

@dataclass
class Longinus(WeaponSkill):
  name: str = "Longinus"
  desc: str = "A legendary lance."
  element: str = "lance"
  rare: bool = True
  color: tuple = PINK
  cost: int = 2
  st: int = 11
  users: tuple[Core] = (Knight,)
  blocks: tuple = (
    (0, 2),
    (1, 0),
    (1, 1),
    (1, 2)
  )

  def render(weapon):
    return use_assets().sprites["icon16_lance"]
