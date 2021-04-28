from skills import Skill

class Bash(Skill):
  name = "Bash"
  kind = "weapon"
  element = "beast"
  desc = "Smashes targets with brute force"
  cost = 1
  st = 0
  users = ()
  blocks = (
    (0, 0),
    (1, 0)
  )
