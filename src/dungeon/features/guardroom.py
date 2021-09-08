from dungeon.features.specialroom import SpecialRoom
from dungeon.props.door import Door
from dungeon.actors.guard import GuardActor
from colors.palette import ORANGE, GREEN, BLUE
from anims.pause import PauseAnim
from anims.flicker import FlickerAnim
from contexts.cutscene import CutsceneContext
from vfx.alertbubble import AlertBubble

class GuardRoom(SpecialRoom):
  def __init__(room, *args, **kwargs):
    super().__init__(degree=2, shape=[
      ".....",
      ".....",
      ".....",
      ".....",
    ], elems=[
      ((2, 0), GuardActor(
        name="Lewis",
        faction="ally",
        facing=(0, 1),
        message=lambda ctx: [
          (ctx.talkee.name, "I cannot let you pass."),
          (ctx.talkee.name, "Suck my dick !"),
        ])
      ),
    ], *args, **kwargs)
    room.entered = False

  def get_edges(room):
    room_width, room_height = room.get_size()
    room_x, room_y = room.cell or (0, 0)
    return [
      # (room_x + room_width // 2, room_y - 1),
      (room_x + room_width // 2, room_y + room.get_height())
    ]

  def place(room, stage, *args, **kwargs):
    if not super().place(stage, *args, **kwargs):
      return False
    room_width, room_height = room.get_size()
    room_x, room_y = room.cell or (0, 0)
    top_edge = (room_x + room_width // 2, room_y - 1)
    stage.set_tile_at(top_edge, stage.FLOOR)
    stage.spawn_elem_at(top_edge, Door())
    return True
