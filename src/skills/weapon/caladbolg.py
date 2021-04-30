from skills.weapon.rare import RareWeapon
from cores import Core
from cores.knight import Knight
from assets import load as use_assets

class Caladbolg(RareWeapon):
  name = "Caladbolg"
  desc = "A legendary blade."
  element = "sword"
  cost = 2
  st = 14
  users = (Knight,)
  blocks = (
    (1, 0),
    (1, 1),
    (1, 2),
    (0, 1),
    (2, 1),
  )

  def render():
    return use_assets().sprites["icon16_sword"]
