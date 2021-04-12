import pygame

class InventoryContext:
  def __init__(ctx, inventory):
    ctx.inventory = inventory
    ctx.cursor = (0, 0)

  def handle_keydown(ctx, key):
    key_deltas = {
      pygame.K_LEFT: (-1, 0),
      pygame.K_RIGHT: (1, 0),
      pygame.K_UP: (0, -1),
      pygame.K_DOWN: (0, 1)
    }
    if key in key_deltas:
      ctx.handle_move(delta)

  def handle_move(ctx, delta):
    delta_x, delta_y = key_deltas[key]
    cursor_x, cursor_y = ctx.cursor
    new_x, new_y = (cursor_x + delta_x, cursor_y + delta_y)
    if new_x >= 0 and new_x < ctx.inventory.cols and new_y >= 0 and new_y < ctx.inventory.rows:
      ctx.cursor = (new_x, new_y)

  def render(ctx, surface):
    pass
