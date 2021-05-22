from skills.weapon.rare import RareWeapon
from cores import Core
from cores.knight import KnightCore
from assets import load as use_assets
from palette import PINK

class Longinus(RareWeapon):
  name = "Longinus"
  desc = "A legendary lance."
  element = "lance"
  cost = 2
  st = 11
  users = (KnightCore,)
  blocks = (
    (0, 2),
    (1, 0),
    (1, 1),
    (1, 2)
  )

  def render(item=None):
    return use_assets().sprites["icon16_lance"]
