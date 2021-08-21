from game.data import GameData
from items.hp.potion import Potion
from config import INVENTORY_COLS, INVENTORY_ROWS

def test_obtain():
  store = GameData()
  obtained = store.obtain_item(Potion)
  assert obtained
  assert Potion in store.items

def test_obtain_full():
  store = GameData(items=[Potion] * INVENTORY_COLS * INVENTORY_ROWS)
  obtained = store.obtain_item(Potion)
  assert not obtained

def test_discard():
  store = GameData(items=[Potion])
  discarded = store.discard_item(Potion)
  assert discarded
  assert Potion not in store.items
