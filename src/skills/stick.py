from skills import Skill
from actors.knight import Knight

class Stick(Skill):
  name = "Stick"
  kind = "weapon"
  element = "lance"
  desc = "A makeshift weapon"
  rare = False
  cost = 1
  st = 2
  users = (Knight,)
  blocks = (
    (0, 0),
    (1, 0)
  )
