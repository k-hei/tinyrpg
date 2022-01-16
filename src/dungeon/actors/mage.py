from dungeon.actors import DungeonActor
from cores.mage import Mage as MageCore
from helpers.mage import step_move, view_mage
from anims.jump import JumpAnim
from anims.walk import WalkAnim
from skills.magic.glacio import Glacio
from skills.magic.congelatio import Congelatio
from skills.magic.roulette import Roulette
from skills.magic.accerso import Accerso
from skills.weapon.broadsword import BroadSword

class Mage(DungeonActor):
  drops = [BroadSword]

  def __init__(mage, core=None, faction="ally", ailment=None, ailment_turns=0, *args, **kwargs):
    super().__init__(
      core=core or MageCore(faction=faction, skills=[Glacio, Accerso], *args, **kwargs),
      ailment=ailment,
      ailment_turns=ailment_turns,
      aggro=3,
      behavior="guard" if faction == "ally" else "chase"
    )

  def encode(mage):
    [cell, kind, *props] = super().encode()
    return [cell, kind, {
      **(props[0] if props else {}),
      **(mage.charge_skill and { "charge_skill": mage.charge_skill } or {}),
      **(mage.charge_dest and { "charge_dest": mage.charge_dest } or {}),
      **(mage.charge_turns and { "charge_turns": mage.charge_turns } or {})
    }]

  @DungeonActor.faction.setter
  def faction(mage, faction):
    DungeonActor.faction.fset(mage, faction)

    if faction == "enemy":
      mage.hp_max *= 6
      mage.hp = mage.hp_max
    else:
      mage.hp_max = mage.core.get_hp_max()

    if faction in ("player", "enemy"):
      mage.behavior = "chase"
    else:
      mage.behavior = "guard"

  def spawn(mage, stage, cell):
    super().spawn(stage, cell)
    mage.faction = mage.faction

  def charge(mage, *args, **kwargs):
    super().charge(*args, **kwargs)
    mage.core.anims.append(MageCore.CastAnim())

  def start_move(actor, running):
    actor.anims = [WalkAnim(period=30 if running else 60)]
    actor.core.anims = actor.anims.copy()

  def stop_move(actor):
    actor.anims = []
    actor.core.anims = []

  def animate_brandish(actor, on_end=None):
    return [
      JumpAnim(
        target=actor,
        height=28,
        delay=actor.core.BrandishAnim.frames_duration[0],
        duration=actor.core.BrandishAnim.jump_duration,
      ),
      actor.core.BrandishAnim(
        target=actor,
        on_end=lambda: (
          actor.stop_move(),
          actor.core.anims.append(actor.core.IdleDownAnim()),
          on_end and on_end(),
        )
      )
    ]

  def step(mage, game):
    if mage.behavior == "guard":
      return None

    enemy = game.find_closest_enemy(mage)
    if not mage.aggro:
      return super().step(game)
    if enemy is None:
      return None

    mage_x, mage_y = mage.cell
    enemy_x, enemy_y = enemy.cell
    dist_x = enemy_x - mage_x
    delta_x = dist_x // (abs(dist_x) or 1)
    dist_y = enemy_y - mage_y
    delta_y = dist_y // (abs(dist_y) or 1)

    mage.face(enemy.cell)
    if (delta_x == 0 and dist_y <= Glacio.range_max
    or delta_y == 0 and dist_x <= Glacio.range_max
    ) and not enemy.ailment == "freeze" and not abs(dist_x) + abs(dist_y) == 1:
      if mage.hp < mage.hp_max / 2:
        mage.charge(skill=Congelatio, dest=enemy.cell)
      else:
        mage.charge(skill=Glacio)
      return game.comps.minilog.print((mage.token(), " is chanting."))

    has_allies = next((e for c in game.room.get_cells() for e in game.stage.get_elems_at(c) if (
      e
      and e is not mage
      and isinstance(e, DungeonActor)
      and e.faction == mage.faction
    )), None)

    if not has_allies:
      mage.charge(skill=Roulette)
      return game.comps.minilog.print((mage.token(), " is chanting."))

    return step_move(mage, game)

  def view(mage, anims):
    return view_mage(mage, anims)
