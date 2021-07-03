from comps.log import Token
from anims.pause import PauseAnim
from cores import Core
from palette import BLACK

class Skill:
  name = "Untitled"
  desc = "No description given."
  kind = None
  element = None
  cost = 1
  range_type = "linear"
  range_min = 1
  range_max = 1
  range_radius = 0
  users = ()
  blocks = ((0, 0),)
  color = BLACK

  def effect(user, dest, game, on_end=None):
    user_x, user_y = user.cell
    facing_x, facing_y = user.facing
    target_cell = (user_x + facing_x, user_y + facing_y)
    game.anims.append([
      PauseAnim(duration=90, on_end=lambda: (
        game.log.print("But nothing happened..."),
        on_end and on_end()
      )
    )])
    return target_cell

  def token(skill):
    return Token(skill.name, skill.color)

  def text(skill):
    tag = skill.element or skill.kind
    text = tag[0].upper() + tag[1:] + ": " + skill.desc
    if skill.cost:
      text += " ({} SP)".format(skill.cost)
    return text

def get_skill_order(skill):
  return [
    "weapon",
    "attack",
    "magic",
    "support",
    "ailment",
    "field",
    "armor"
  ].index(skill.kind)
