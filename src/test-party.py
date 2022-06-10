from game.store import GameStore
from dungeon.context import DungeonContext
from town.sideview.context import SideViewContext
from town.sideview.actor import Actor as SideViewActor
from town.topview.context import TopViewContext
from town.topview.actor import Actor as TopViewActor
from cores.knight import Knight
from cores.mage import Mage

knight = Knight()
mage = Mage()

def test_switch_one():
  store = GameStore(party=[knight])
  store.switch_chars()
  assert store.party[0] is knight

def test_switch_two():
  store = GameStore(party=[knight, mage])
  store.switch_chars()
  assert store.party[0] is mage
  assert store.party[1] is knight

def test_switch_two_from_town_sideview():
  store = GameStore(party=[knight, mage])
  ctx = SideViewContext(store)
  ctx.switch_chars()
  assert ctx.store.party[0] is mage
  assert ctx.store.party[1] is knight
  assert ctx.party[0].core is mage
  assert ctx.party[1].core is knight

def test_switch_two_from_town_topview():
  store = GameStore(party=[knight, mage])
  ctx = TopViewContext(store)
  ctx.switch_chars()
  assert ctx.store.party[0] is mage
  assert ctx.store.party[1] is knight
  assert ctx.party[0].core is mage
  assert ctx.party[1].core is knight

def test_switch_two_from_dungeon():
  dungeon = DungeonContext(store=GameStore(party=[knight, mage]))
  dungeon.switch_chars()
  assert dungeon.store.party[0] is mage
  assert dungeon.store.party[1] is knight
  assert dungeon.party[0].core is mage
  assert dungeon.party[1].core is knight

def test_recruit():
  store = GameStore(party=[knight])
  store.recruit(mage)
  assert store.party[1] is mage
  assert "Mage" in store.builds

def test_recruit_from_town_sideview():
  store = GameStore(party=[knight])
  ctx = SideViewContext(store)
  ctx.recruit(SideViewActor(core=mage))
  assert ctx.party[1].core is mage
  assert store.party[1] is mage

def test_recruit_from_town_topview():
  store = GameStore(party=[knight])
  ctx = TopViewContext(store)
  ctx.recruit(TopViewActor(core=mage))
  assert ctx.party[1].core is mage
  assert store.party[1] is mage
