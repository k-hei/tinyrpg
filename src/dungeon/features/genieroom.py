from dungeon.features.specialroom import SpecialRoom
from dungeon.props.door import Door
from dungeon.actors.genie import Genie as GenieActor
from palette import ORANGE, GREEN, BLUE
from anims.pause import PauseAnim
from anims.flicker import FlickerAnim
from contexts.cutscene import CutsceneContext
from vfx.alertbubble import AlertBubble

class GenieRoom(SpecialRoom):
  def __init__(room, *args, **kwargs):
    super().__init__(degree=2, shape=[
      "###·###",
      "  ·····",
      "  ·····",
      "  ·····",
      "  .../·",
      "  .....",
      "  .....",
    ], elems=[
      ((2, 1), GenieActor(name="Joshin", script=[], color=BLUE)),
      ((4, 2), GenieActor(name="Brajin", script=[], color=GREEN)),
      ((3, 3), GenieActor(name="Doshin", script=[], color=ORANGE)),
    ], *args, **kwargs)
    room.entered = False

  def get_edges(room):
    room_width, room_height = room.get_size()
    room_x, room_y = room.cell or (0, 0)
    return [
      # (room_x + room_width // 2, room_y - 1),
      (room_x + room_width // 2, room_y + room.get_height())
    ]

  def on_enter(room, game):
    if room.entered:
      return
    room.entered = True
    genies = [e for e in [game.floor.get_elem_at(c, superclass=GenieActor) for c in room.get_cells()] if e]
    game.open(CutsceneContext(script=lambda game: [
      lambda step: (
        game.camera.focus((4, 2), speed=8),
        game.anims.append([(lambda i, g: (
          g is not genies[-1] and FlickerAnim(
            target=g,
            duration=30,
            delay=60 + 20 * i,
            on_end=lambda: game.floor.remove_elem(g)
          ) or PauseAnim(
            duration=60 + 20 * i + 15,
            on_end=step
          )
        ))(i, g) for i, g in enumerate(genies)])
      ),
      lambda step: (
        game.vfx.append(AlertBubble(cell=(genies[-1].cell[0], genies[-1].cell[1] - genies[-1].elev))),
        game.anims.append([PauseAnim(duration=15, on_end=step)])
      ),
      lambda step: (
        genies[-1].face((genies[-1].cell[0] - 1, genies[-1].cell[1])),
        game.anims.append([PauseAnim(duration=30, on_end=step)])
      ),
      lambda step: (
        genies[-1].face((genies[-1].cell[0] + 1, genies[-1].cell[1])),
        game.anims.append([PauseAnim(duration=30, on_end=step)])
      ),
      lambda step: game.anims.append([FlickerAnim(
        target=genies[-1],
        duration=30,
        on_end=step
      )]),
      lambda step: (
        game.floor.remove_elem(genies[-1]),
        game.anims.append([PauseAnim(
          duration=15,
          on_end=step
        )])
      ),
      lambda step: (
        game.camera.blur(),
        game.anims.append([PauseAnim(
          duration=15,
          on_end=step
        )])
      )
    ]))

  def place(room, stage, connectors, cell=None):
    super().place(stage, connectors, cell=None)
    room_width, room_height = room.get_size()
    room_x, room_y = cell or room.cell or (0, 0)
    top_edge = (room_x + room_width // 2, room_y - 1)
    stage.set_tile_at(top_edge, stage.FLOOR_ELEV)
    stage.spawn_elem_at(top_edge, Door())
