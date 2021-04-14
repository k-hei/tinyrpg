from dataclasses import dataclass
from typing import Dict
import json
import pygame
from pygame import Surface
from text import Font

@dataclass
class Assets:
  sprites: Dict[str, Surface]
  fonts: Dict[str, Font]

assets = None
sprite_paths = {
  "font_standard": "assets/fonts/standard/typeface.png",
  "font_smallcaps": "assets/fonts/smallcaps/typeface.png",
  "cursor": "assets/cursor.png",
  "cursor_cell": "assets/cursor-cell.png",
  "cursor_cell1": "assets/cursor-cell1.png",
  "cursor_cell2": "assets/cursor-cell2.png",
  "knight": "assets/knight.png",
  "knight_walk": "assets/knight-walk.png",
  "knight_flinch": "assets/knight-flinch.png",
  "mage": "assets/mage.png",
  "mage_walk": "assets/mage-walk.png",
  "mage_flinch": "assets/mage-flinch.png",
  "bat": "assets/bat.png",
  "rat": "assets/rat.png",
  "floor": "assets/floor.png",
  "wall": "assets/wall.png",
  "wall_base": "assets/wall-base.png",
  "chest": "assets/chest.png",
  "chest_open": "assets/chest-open.png",
  "chest_open1": "assets/chest-open1.png",
  "chest_open2": "assets/chest-open2.png",
  "chest_open3": "assets/chest-open3.png",
  "chest_open4": "assets/chest-open4.png",
  "stairs_up": "assets/stairs-up.png",
  "stairs_down": "assets/stairs-down.png",
  "door": "assets/door.png",
  "door_open": "assets/door-open.png",
  "eye": "assets/eye.png",
  "eye_flinch": "assets/eye-flinch.png",
  "eye_attack": "assets/eye-attack.png",
  "tag_hp": "assets/hp.png",
  "tag_sp": "assets/sp.png",
  "log": "assets/log.png",
  "portrait_knight": "assets/portrait-knight.png",
  "portrait_mage": "assets/portrait-mage.png",
  "icon_shield": "assets/icon-shield.png",
  "icon_hat": "assets/icon-hat.png",
  "icon_axe": "assets/icon-axe.png",
  "icon_lance": "assets/icon-lance.png",
  "icon_skill": "assets/icon-skill.png",
  "icon_potion": "assets/icon-potion.png",
  "icon_bread": "assets/icon-bread.png",
  "icon_fish": "assets/icon-fish.png",
  "icon_cheese": "assets/icon-cheese.png",
  "icon_emerald": "assets/icon-emerald.png",
  "icon_ankh": "assets/icon-ankh.png",
  "icon_stairs": "assets/icon-stairs.png",
  "skill": "assets/skill.png",
  "box": "assets/box.png",
  "bar": "assets/bar.png",
  "hud": "assets/hud.png",
  "statusbar": "assets/statusbar.png"
}

def load():
  global assets
  if assets is None:
    sprites = {}
    fonts = {}
    for name, path in sprite_paths.items():
      sprites[name] = pygame.image.load(path).convert_alpha()
    meta_standard = json.loads(open("assets/fonts/standard/metadata.json", "r").read())
    meta_smallcaps = json.loads(open("assets/fonts/smallcaps/metadata.json", "r").read())
    fonts["standard"] = Font(sprites["font_standard"], **meta_standard)
    fonts["smallcaps"] = Font(sprites["font_smallcaps"], **meta_smallcaps)
    assets = Assets(sprites, fonts)
  return assets
