from contexts.app import App
from contexts.custom import CustomContext
from savedata.resolve import resolve_skill
from cores.knight import Knight
from config import KNIGHT_BUILD

knight = Knight()
App(title="equip menu demo",
  context=CustomContext(
    skills=[resolve_skill(s) for s in ["Stick", "Blitzritter", "Counter"]],
    chars=[knight],
    builds={
      knight: [(resolve_skill(s), p) for s, p in KNIGHT_BUILD.items()]
    }
  )
).init()
