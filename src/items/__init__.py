import palette

def get_color(item):
  if item.kind == "hp": return palette.RED
  if item.kind == "sp": return palette.BLUE
  if item.kind == "dungeon": return palette.GREEN
  if item.kind == "ailment": return palette.PURPLE
