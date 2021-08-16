from unittest import TestCase, main
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

class TestRecruit(TestCase):
  def test_recruit_from_store(test):
    store = GameData(party=[knight])
    store.recruit(mage)
    test.assertIs(store.party[1], mage)

  def test_recruit_from_town_sideview(test):
    store = GameData(party=[knight])
    ctx = SideViewContext(store)
    ctx.recruit(SideViewActor(core=mage))
    test.assertIs(ctx.party[1].core, mage)
    test.assertIs(store.party[1], mage)

  def test_recruit_from_town_topview(test):
    store = GameData(party=[knight])
    ctx = TopViewContext(store)
    ctx.recruit(TopViewActor(core=mage))
    test.assertIs(ctx.party[1].core, mage)
    test.assertIs(store.party[1], mage)

if __name__ == "__main__":
  main()
