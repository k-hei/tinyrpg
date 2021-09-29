import lib.vector as vector
from anims.attack import AttackAnim
from anims.pause import PauseAnim

def sequence_mage_bump(room, game):
  altar = room.altar
  mage = room.mage
  return [
    lambda step: game.anims.extend([
      [AttackAnim(
        target=mage,
        src=mage.cell,
        dest=vector.add(mage.cell, mage.facing)
      )],
      [PauseAnim(duration=15, on_end=step)]
    ])
  ]
