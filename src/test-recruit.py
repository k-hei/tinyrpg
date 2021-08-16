from game.data import GameData
from game.context import GameContext
from town.context import TownContext
from town.sideview.context import SideViewContext
from town.sideview.actor import Actor as SideViewActor
from town.topview.context import TopViewContext
from town.topview.actor import Actor as TopViewActor
from cores.knight import Knight
from cores.mage import Mage

knight = Knight()
mage = Mage()

def test_recruit():
  store = GameData(party=[knight])
  store.recruit(mage)
  assert store.party[1] is mage
  assert "Mage" in store.builds

def test_recruit_from_town_sideview():
  store = GameData(party=[knight])
  ctx = SideViewContext(store)
  ctx.recruit(SideViewActor(core=mage))
  assert ctx.party[1].core is mage
  assert store.party[1] is mage

def test_recruit_from_town_topview():
  store = GameData(party=[knight])
  ctx = TopViewContext(store)
  ctx.recruit(TopViewActor(core=mage))
  assert ctx.party[1].core is mage
  assert store.party[1] is mage
