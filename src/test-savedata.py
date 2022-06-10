from game.store import GameStore
from savedata import load

store = GameStore()
savedata = load("src/data00.json")

def test_encode():
  savedata = GameStore.encode(store)
  assert bool(savedata)

def test_decode():
  store = GameStore.decode(savedata)
  assert bool(store)
