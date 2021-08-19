from contexts.app import App
from game.context import GameContext
from savedata import load
from dungeon.features.battleroom import BattleRoom

App(title="battle room demo",
  context=GameContext(
    savedata=load("src/data00.json"),
    feature=BattleRoom
  )
).init()
