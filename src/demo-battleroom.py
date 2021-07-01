from contexts.app import App
from contexts.game import GameContext
from savedata import load
from dungeon.features.battleroom import BattleRoom

App(title="battle room demo",
  context=GameContext(
    savedata=load("src/data0.json"),
    feature=BattleRoom
  )
).init()
