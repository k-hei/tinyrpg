from dataclasses import dataclass
from skills.weapon import WeaponSkill

@dataclass
class Tackle(WeaponSkill):
  name: str = "Tackle"
  desc: str = "Smashes targets with brute force"
  element: str = "beast"
