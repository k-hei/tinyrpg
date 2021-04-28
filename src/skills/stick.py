from skills import Skill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
import math
from actors.knight import Knight

ATTACK_DURATION = 12

class Stick(Skill):
  name = "Stick"
  kind = "weapon"
  element = "lance"
  desc = "A makeshift weapon"
  cost = 1
  st = 2
  users = (Knight,)
  blocks = (
    (0, 0),
    (1, 0)
  )
