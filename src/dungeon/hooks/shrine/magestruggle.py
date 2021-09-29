import lib.vector as vector
from anims.jump import JumpAnim
from anims.pause import PauseAnim

def sequence_mage_struggle(room, game):
  altar = room.altar
  mage = room.mage
  return [
    lambda step: (
      setattr(mage, "cell", vector.add(altar.cell, (0, 1))),
      setattr(mage, "facing", (0, -1)),
      game.anims.append([
        JumpAnim(target=mage),
        PauseAnim(duration=30, on_end=step)
      ])
    ),
    lambda step: (
      setattr(mage, "cell", vector.add(altar.cell, (1, 0))),
      setattr(mage, "facing", (-1, 0)),
      game.anims.append([
        JumpAnim(target=mage),
        PauseAnim(duration=30, on_end=step)
      ])
    ),
    lambda step: (
      setattr(mage, "cell", vector.add(altar.cell, (-1, -1))),
      setattr(mage, "facing", (1, 0)),
      game.anims.append([
        JumpAnim(target=mage),
        PauseAnim(duration=30, on_end=step)
      ])
    ),
  ]
