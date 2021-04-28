from skills import Skill
from actors.knight import Knight

ATTACK_DURATION = 12

class Club(Skill):
  name = "Club"
  kind = "weapon"
  element = "axe"
  desc = "A makeshift weapon"
  cost = 1
  st = 2
  users = (Knight,)
  blocks = (
    (0, 0),
    (1, 0)
  )
