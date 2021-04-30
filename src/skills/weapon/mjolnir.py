from skills.weapon.rare import RareWeapon
from cores import Core
from cores.knight import Knight
from assets import load as use_assets
from palette import PINK

class Mjolnir(RareWeapon):
  name = "Mjolnir"
  desc = "A legendary hammer."
  element = "axe"
  cost = 3
  st = 16
  users = (Knight,)
  blocks = (
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1)
  )

  def render():
    return use_assets().sprites["icon16_axe"]
