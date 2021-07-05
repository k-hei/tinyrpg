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

def find_skill_targets(skill, user, floor=None):
  targets = []
  user_x, user_y = user.cell
  facing_x, facing_y = user.facing
  cursor = (user_x + facing_x, user_y + facing_y)
  if skill is None:
    return []
  if skill.range_type == "row":
    if facing_x:
      targets += [
        (user_x + facing_x, user_y - 1),
        (user_x + facing_x, user_y),
        (user_x + facing_x, user_y + 1)
      ]
    elif facing_y:
      targets += [
        (user_x - 1, user_y + facing_y),
        (user_x, user_y + facing_y),
        (user_x + 1, user_y + facing_y)
      ]
  if skill.range_type == "radial" or skill.range_type == "linear" and skill.range_max == 1:
    if skill.range_min == 0:
      targets.append((user_x, user_y))
    targets.extend([
      (user_x, user_y - 1),
      (user_x - 1, user_y),
      (user_x + 1, user_y),
      (user_x, user_y + 1)
    ])
  elif skill.range_type == "linear" and skill.range_max > 2:
    targets.append(cursor)
    is_blocked = False
    r = 1
    while not is_blocked and r < skill.range_max:
      if floor and (floor.get_tile_at(cursor).solid or floor.get_elem_at(cursor)):
        is_blocked = True
      else:
        cursor_x, cursor_y = cursor
        cursor = (cursor_x + facing_x, cursor_y + facing_y)
        targets.append(cursor)
      r += 1
  elif skill.range_type == "linear":
    for r in range(skill.range_min, skill.range_max + 1):
      targets.append((user_x + facing_x * r, user_y + facing_y * r))
  return targets

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
