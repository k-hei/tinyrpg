from skills import Skill
from actors.knight import Knight
from assets import load as use_assets

class Caladbolg(Skill):
  name = "Caladbolg"
  kind = "weapon"
  element = "sword"
  desc = "A legendary blade."
  rare = True
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
