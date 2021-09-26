from lib.cell import add as add_vector

def on_place(room, stage):
  stage.entrance = add_vector(room.center, (-1, 1))
