import palette
from comps.log import Token
from anims.pause import PauseAnim

class Skill:
  name = None
  kind = None
  element = None
  desc = None
  cost = 0
  range_type = "linear"
  range_min = 1
  range_max = 1
  range_radius = 0
  hp = 0
  st = 0
  users = ()
  blocks = (
    (0, 0),
  )

  def effect(user, game, on_end=None):
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

def get_sort_order(skill):
  return ["attack", "magic", "support", "ailment", "field", "passive"].index(skill.kind)

def get_skill_text(skill):
  tag = skill.element or skill.kind
  text = tag[0].upper() + tag[1:]
  text += ': ' + skill.desc
  if skill.cost:
    text += " (" + str(skill.cost) + " SP)"
  return text

def get_skill_color(skill):
  if skill.kind == "attack": return palette.RED
  if skill.kind == "magic": return palette.BLUE
  if skill.kind == "support": return palette.GREEN
  if skill.kind == "ailment": return palette.PURPLE
  if skill.kind == "field": return palette.GOLD
  if skill.kind == "passive": return palette.GOLD
  if skill.kind == "weapon" and skill.element == "beast": return palette.BLACK
  if skill.kind == "weapon": return palette.GOLD

def  get_skill_token(skill):
  return Token(skill.name, get_skill_color(skill))
