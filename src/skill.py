class Skill():
  def __init__(skill, name, cost):
    skill.name = name
    skill.cost = cost

  def perform(skill, user, game):
    if game.sp < skill.cost:
      return False
    game.sp = max(0, game.sp - skill.cost)
    return True
