from skills.weapon import WeaponSkill
from cores import Core
from dungeon.actors.knight import Knight
from assets import load as use_assets

class Caladbolg(WeaponSkill):
  name: str = "Caladbolg"
  desc: str = "A legendary blade."
  element: str = "sword"
  rare: bool = True
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

  def render():
    return use_assets().sprites["icon16_sword"]
