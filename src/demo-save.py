from contexts.app import App
from contexts.save import SaveContext
from savedata import GameState
from config import KNIGHT_BUILD

App(title="save data demo",
  context=SaveContext(GameState(
    place="town",
    sp=40,
    time=0,
    gold=100,
    items=["Potion", "Emerald"],
    skills=["Stick", "Blitzritter"],
    party=["knight"],
    chars={"knight": KNIGHT_BUILD}
  ))
).init()
