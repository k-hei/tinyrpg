from contexts.app import App
from contexts.skill import SkillContext
from skills.weapon.stick import Stick
from skills.attack.blitzritter import Blitzritter
from skills.support.counter import Counter

App(title="skill menu demo",
  context=SkillContext(skills=[Stick, Blitzritter, Counter])
).init()
