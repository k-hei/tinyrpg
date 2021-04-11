class DungeonContext:
  def __init__(ctx):
    ctx.floor = None
    ctx.floors = [] # map of floors -> tiles
    ctx.sp_max = 40
    ctx.sp = ctx.sp_max
    pass

  def ascend(ctx):
    index = ctx.floors.index(ctx.floor) + 1
    if index < len(ctx.floors):
      ctx.floor = ctx.floors[index]
    else:
      ctx.floor = gen.dungeon((19, 19))
      ctx.floors.append(ctx.floor)
    return True

  def descend(ctx):
    index = ctx.floors.index(ctx.floor) - 1
    if index >= 0:
      ctx.floor = ctx.floors[index]
      return True
    else:
      return False
