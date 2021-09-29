from anims.pause import PauseAnim

def sequence_mage_spin(room, game):
  mage = room.mage
  return [
    lambda step: (
      setattr(mage, "facing", (0, -1)),
      game.anims.append([PauseAnim(duration=5, on_end=step)])
    ),
    lambda step: (
      setattr(mage, "facing", (-1, 0)),
      game.anims.append([PauseAnim(duration=5, on_end=step)])
    ),
    lambda step: (
      setattr(mage, "facing", (0, 1)),
      game.anims.append([PauseAnim(duration=5, on_end=step)])
    ),
    lambda step: (
      setattr(mage, "facing", (1, 0)),
      game.anims.append([PauseAnim(duration=5, on_end=step)])
    ),
  ]
