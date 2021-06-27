from dungeon.props import Prop
from assets import load as use_assets
from anims.move import MoveAnim

class Block(Prop):
  def effect(block, game):
    hero = game.hero
    block_x, block_y = block.cell
    delta_x, delta_y = hero.facing
    target_cell = (block_x + delta_x, block_y + delta_y)
    target_tile = game.floor.get_tile_at(target_cell)
    target_elem = game.floor.get_elem_at(target_cell)
    if target_tile is None or target_tile.solid or target_elem:
      return None
    game.anims.append([
      MoveAnim(
        duration=45,
        target=hero,
        src=hero.cell,
        dest=block.cell
      ),
      MoveAnim(
        duration=45,
        target=block,
        src=block.cell,
        dest=target_cell
      )
    ])
    hero.cell = block.cell
    block.cell = target_cell
    return False

  def view(block, anims):
    return super().view(use_assets().sprites["pushblock"], anims)
