from game.store import GameStore
from items.hp.potion import Potion
from config import INVENTORY_COLS, INVENTORY_ROWS

def test_obtain():
  store = GameStore()
  obtained = store.obtain_item(Potion)
  assert obtained
  assert Potion in store.items

def test_obtain_full():
  store = GameStore(items=[Potion] * INVENTORY_COLS * INVENTORY_ROWS)
  obtained = store.obtain_item(Potion)
  assert not obtained

def test_discard():
  store = GameStore(items=[Potion])
  discarded = store.discard_item(Potion)
  assert discarded
  assert Potion not in store.items
