from skills import Skill
from actors.knight import Knight
from assets import load as use_assets

class Longinus(Skill):
  name = "Longinus"
  kind = "weapon"
  element = "lance"
  desc = "A legendary lance."
  rare = True
  cost = 2
  st = 11
  users = (Knight,)
  blocks = (
    (0, 2),
    (1, 0),
    (1, 1),
    (1, 2)
  )

  def render():
    return use_assets().sprites["icon16_lance"]
