from dataclasses import dataclass
from items.equipment import EquipmentItem
from skills import Skill
from skills.weapon.rustyblade import RustyBlade as RustyBladeSkill

@dataclass
class RustyBlade(EquipmentItem):
  name: str = "RustyBlade"
  desc: str = RustyBladeSkill.desc
  skill: Skill = RustyBladeSkill
  sprite: str = "rustysword"
