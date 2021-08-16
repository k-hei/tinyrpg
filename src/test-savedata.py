from unittest import TestCase, main
from game.data import GameData
from savedata import load

store = GameData()
savedata = load("src/data00.json")

class TestSaveData(TestCase):
  def test_encode(test):
    savedata = GameData.encode(store)
    test.assertTrue(not not savedata)

  def test_decode(test):
    store = GameData.decode(savedata)
    test.assertTrue(not not store)

if __name__ == "__main__":
  main()
