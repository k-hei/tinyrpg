from dataclasses import dataclass
from collections.abc import Sequence
from comps.hud import Hud
from comps.minimap import Minimap
from comps.minilog import Minilog
from comps.miniskill import Miniskill as SkillBadge
from comps.skillbanner import SkillBanner
from comps.spmeter import SpMeter
from comps.floorno import FloorNo

@dataclass
class ComponentStore(Sequence):
  hud: Hud
  minimap: Minimap
  minilog: Minilog
  skill_badge: SkillBadge
  skill_banner: SkillBanner
  sp_meter: SpMeter
  floor_no: FloorNo

  def __post_init__(store):
    store._comps = [
      store.hud,
      store.minimap,
      store.minilog,
      store.skill_badge,
      store.skill_banner,
      store.sp_meter,
      store.floor_no
    ]

  def __getitem__(store, index):
    return store._comps[index]

  def __len__(store):
    return len(store._comps)
