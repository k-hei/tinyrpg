class Skill:
  def __init__(skill, name, kind, desc, cost, radius):
    skill.name = name
    skill.kind = kind
    skill.desc = desc
    skill.cost = cost
    skill.radius = radius

  def effect(skill, game):
    if game.sp >= skill.cost:
      game.sp -= skill.cost
