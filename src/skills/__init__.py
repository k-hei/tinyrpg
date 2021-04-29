from dataclasses import dataclass
from comps.log import Token
from anims.pause import PauseAnim
from cores import Core
from palette import BLACK

@dataclass
class Skill:
  name: str = ""
  desc: str = ""
  element: str = ""
  rare: bool = False
  cost: int = 0
  users: tuple[Core] = ()
  blocks: tuple[tuple[int, int]] = ((0, 0),)
  color: tuple[int, int, int] = BLACK

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

  def token(skill):
    return Token(skill.name, skill.color)

def get_skill_order(skill):
  skill_type = type(skill).__name__
  return [
    "WeaponSkill",
    "AttackSkill",
    "MagicSkill",
    "SupportSkill",
    "AilmentSkill",
    "FieldSkill",
    "ArmorSkill"
  ].index(skill_type)

def get_skill_text(skill):
  tag = skill.element or skill.kind
  text = tag[0].upper() + tag[1:] + ": " + skill.desc
  if skill.cost:
    text += " ({} SP)".format(skill.cost)
  return text

def get_skill_color(skill):
  if skill.kind == "attack": return palette.RED
  if skill.kind == "magic": return palette.BLUE
  if skill.kind == "support": return palette.GREEN
  if skill.kind == "ailment": return palette.PURPLE
  if skill.kind == "field": return palette.GOLD
  if skill.kind == "passive": return palette.GOLD
  if skill.kind == "weapon" and skill.element == "beast": return palette.BLACK
  if skill.kind == "weapon" and skill.rare: return palette.PINK
  if skill.kind == "weapon": return palette.GRAY
