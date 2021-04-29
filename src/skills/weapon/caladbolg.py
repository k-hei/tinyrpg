from dataclasses import dataclass
from skills.weapon import WeaponSkill
from cores import Core
from cores.knight import Knight
from assets import load as use_assets
from palette import PINK

@dataclass
class Caladbolg(WeaponSkill):
  name: str = "Caladbolg"
  desc: str = "A legendary blade."
  element: str = "sword"
  rare: bool = True
  color: tuple = PINK
  cost: int = 2
  st: int = 14
  users: tuple[Core] = (Knight,)
  blocks: tuple[tuple[int, int]] = (
    (1, 0),
    (1, 1),
    (1, 2),
    (0, 1),
    (2, 1),
  )

  def render(weapon):
    return use_assets().sprites["icon16_sword"]
