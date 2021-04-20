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
  users = ()
  blocks = (
    (0, 0),
  )

  def effect(game):
    game.log.print("But nothing happened...")

def get_sort_order(skill):
  return ["attack", "magic", "support", "ailment", "field", "passive"].index(skill.kind)

def get_skill_text(skill):
  tag = skill.element or skill.kind
  text = tag[0].upper() + tag[1:]
  text += ': ' + skill.desc
  if skill.cost:
    text += " (" + str(skill.cost) + " SP)"
  return text
