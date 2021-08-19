from game.data import GameData
from skills.attack.shieldbash import ShieldBash

def test_learn():
  store = GameData()
  learned = store.learn_skill(ShieldBash)
  assert learned
  assert ShieldBash in store.skills
  assert ShieldBash in store.new_skills

def test_learn_duplicate():
  store = GameData()
  store.learn_skill(ShieldBash)
  learned = store.learn_skill(ShieldBash)
  assert not learned
  assert len(store.skills) == 1
  assert len(store.new_skills) == 1
