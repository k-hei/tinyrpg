from game.data import GameData
from savedata import load

store = GameData()
savedata = load("src/data00.json")

def test_encode():
  savedata = GameData.encode(store)
  assert bool(savedata)

def test_decode():
  store = GameData.decode(savedata)
  assert bool(store)
