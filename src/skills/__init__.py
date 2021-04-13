class Skill:
  def __init__(skill, name, desc, cost):
    skill.name = name
    skill.desc = desc
    skill.cost = cost

  def effect(skill, game):
    if game.sp >= skill.cost:
      game.sp -= skill.cost
