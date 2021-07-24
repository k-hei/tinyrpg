from comps.log import Token
from anims.pause import PauseAnim
from cores import Core
from colors.palette import BLACK
from lib.cell import neighborhood

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

  def find_targets(skill, user, floor=None, dest=None):
    user_x, user_y = user.cell
    facing_x, facing_y = tuple(map(int, user.facing))
    if skill.range_radius < 0:
      return []
    if skill.range_type == "row":
      if facing_x:
        return [
          (user_x + facing_x, user_y - 1),
          (user_x + facing_x, user_y),
          (user_x + facing_x, user_y + 1)
        ]
      elif facing_y:
        return [
          (user_x - 1, user_y + facing_y),
          (user_x, user_y + facing_y),
          (user_x + 1, user_y + facing_y)
        ]
    if skill.range_type == "linear" and skill.range_max > 1:
      cursor = (user_x + facing_x, user_y + facing_y)
      targets = [cursor]
      is_blocked = False
      r = 1
      while not is_blocked and r < skill.range_max:
        if floor and not floor.is_cell_empty(cursor):
          is_blocked = True
        else:
          cursor_x, cursor_y = cursor
          cursor = (cursor_x + facing_x, cursor_y + facing_y)
          targets.append(cursor)
        r += 1
      return targets
    if skill.range_radius == 0:
      return [dest]
    return neighborhood(dest, skill.range_radius, inclusive=True) if dest else []

  def find_range(skill, user, floor=None):
    targets = []
    user_x, user_y = user.cell
    facing_x, facing_y = user.facing
    if skill is None:
      return []
    if skill.range_min == 0:
      targets.append((user_x, user_y))
    if (skill.range_type == "row"
    or skill.range_type == "linear" and skill.range_max > 1):
      return Skill.find_targets(skill, user, floor)
    if skill.range_type in ("radial", "linear") and skill.range_max == 1:
      targets += [
        (user_x, user_y - 1),
        (user_x - 1, user_y),
        (user_x + 1, user_y),
        (user_x, user_y + 1)
      ]
    elif skill.range_type == "radial":
      targets += neighborhood(user.cell, radius=skill.range_max)
      if skill.range_min > 1:
        targets = [t for t in targets if t not in neighborhood(user.cell, radius=skill.range_min - 1, inclusive=True)]
    return targets

def get_skill_order(skill):
  return [
    "weapon",
    "armor",
    "attack",
    "magic",
    "support",
    "ailment",
    "field",
  ].index(skill.kind)
