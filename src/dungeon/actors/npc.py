from dungeon.actors import DungeonActor
from assets import load as use_assets

class NPC(DungeonActor):
  def __init__(npc):
    super().__init__(
      name="Gumpert",
      faction="ally",
      hp=0,
      st=0,
      en=0
    )
    npc.messages = [
      ("I've heard there's a hidden room", "somewhere on this floor."),
      ("Not that they've ever let me", "see it...")
    ]
    npc.message = npc.messages[0]

  def render(npc, anims):
    sprites = use_assets().sprites
    sprite = sprites["eye"]
    return super().render(sprite, anims)
