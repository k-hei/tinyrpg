from dataclasses import dataclass
from skills.weapon import WeaponSkill
from cores import Core
from cores.knight import Knight
from assets import load as use_assets
from palette import PINK

@dataclass
class Mjolnir(WeaponSkill):
  name: str = "Mjolnir"
  desc: str = "A legendary hammer."
  element: str = "axe"
  rare: bool = True
  color: tuple = PINK
  cost: int = 3
  st: int = 16
  users: tuple[Core] = (Knight,)
  blocks: tuple = (
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1)
  )

  def render(weapon):
    return use_assets().sprites["icon16_axe"]
