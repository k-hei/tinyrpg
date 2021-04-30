from skills import Skill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from dungeon.stage import Stage
from dungeon.actors.mage import Mage

class DetectMana(Skill):
  name = "DetectMana"
  desc = "Reveals hidden passages"
  kind = "field"
  cost = 1
  range_min = 0
  range_max = 0
  users = (Mage,)
  blocks = (
    (0, 0),
  )

  def effect(user, game, on_end=None):
    floor = game.floor
    camera = game.camera

    def on_wait():
      for cell in user.visible_cells:
        if floor.get_tile_at(cell) is Stage.DOOR_HIDDEN:
          game.log.print("You sense a hidden passageway here!")
          camera.focus(cell)
          game.anims.append([PauseAnim(
            duration=120,
            on_end=on_end
          )])
          break
      else:
        game.log.print("There doesn't seem to be anything nearby.")
        if on_end:
          on_end()

    game.anims.append([PauseAnim(
      duration=30,
      on_end=on_wait
    )])
    return user.cell
