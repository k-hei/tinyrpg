from skills import Skill
from actors.knight import Knight
from assets import load as use_assets

class Mjolnir(Skill):
  name = "Mjolnir"
  kind = "weapon"
  element = "axe"
  desc = "A legendary hammer."
  rare = True
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
