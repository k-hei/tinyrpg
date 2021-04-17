class Skill:
  def __init__(skill, name, kind, element, desc, cost, radius):
    skill.name = name
    skill.kind = kind
    skill.element = element
    skill.desc = desc
    skill.cost = cost
    skill.radius = radius

  def effect(skill, game):
    if game.sp >= skill.cost:
      game.sp -= skill.cost

def get_skill_text(skill):
  tag = skill.element or skill.kind
  text = tag[0].upper() + tag[1:]
  text += ': ' + skill.desc
  text += " (" + str(skill.cost) + " SP)"
  return text
