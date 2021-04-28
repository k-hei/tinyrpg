import config
from contexts import Context
from contexts.dungeon import DungeonContext
from town import TownContext
from transits.dissolve import DissolveIn, DissolveOut

from actors.knight import Knight
from actors.mage import Mage

from inventory import Inventory
from items.potion import Potion
from items.ankh import Ankh
from items.bread import Bread
from items.fish import Fish
from items.emerald import Emerald
from items.balloon import Balloon
from items.antidote import Antidote
from items.elixir import Elixir

from skills.stick import Stick
from skills.blitzritter import Blitzritter
from skills.counter import Counter
from skills.hpup import HpUp
from skills.sana import Sana
from skills.somnus import Somnus
from skills.detectmana import DetectMana

class GameContext(Context):
  def __init__(ctx):
    super().__init__()
    ctx.transits = [DissolveOut(config.WINDOW_SIZE)]
    ctx.inventory = Inventory((2, 4), [
      Potion(), Balloon()
    ])
    ctx.sp_max = 50
    ctx.sp = ctx.sp_max
    ctx.hero = Knight()
    ctx.ally = Mage()
    ctx.new_skills = []
    ctx.skill_pool = [
      Stick,
      Blitzritter,
      Somnus,
      Sana,
      DetectMana,
      HpUp,
    ]
    ctx.skill_builds = {
      ctx.hero: [
        (Stick, (0, 0)),
        (Blitzritter, (1, 0))
      ],
      ctx.ally: [
        (Somnus, (0, 0)),
        (DetectMana, (1, 0))
      ]
    }
    ctx.monster_kills = {}
    ctx.debug = False

  def reset(ctx):
    if type(ctx.child) is DungeonContext:
      ctx.goto_dungeon()
    elif type(ctx.child) is TownContext:
      ctx.goto_town()

  def goto_dungeon(ctx):
    ctx.child = DungeonContext(parent=ctx)

  def goto_town(ctx, returning=False):
    ctx.child = TownContext(parent=ctx, returning=returning)

  def update_skills(ctx):
    ctx.hero.skills = [skill for skill, cell in ctx.skill_builds[ctx.hero]]
    ctx.ally.skills = [skill for skill, cell in ctx.skill_builds[ctx.ally]]

  def dissolve(ctx, on_clear, on_end=None):
    ctx.transits.append(DissolveIn(config.WINDOW_SIZE, on_clear))
    ctx.transits.append(DissolveOut(config.WINDOW_SIZE, on_end))

  def handle_keydown(ctx, key):
    if len(ctx.transits):
      return False
    return super().handle_keydown(key)

  def draw(ctx, surface):
    super().draw(surface)
    if len(ctx.transits):
      transit = ctx.transits[0]
      transit.update()
      transit.draw(surface)
      if transit.done:
        ctx.transits.remove(transit)
