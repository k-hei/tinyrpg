from dataclasses import dataclass
from typing import Dict
import json
import pygame
from pygame import Surface
from text import Font

ASSETS_PATH = "assets/"

@dataclass
class Assets:
  sprites: Dict[str, Surface]
  fonts: Dict[str, Font]

assets = None
sprite_paths = {
  "font_standard": "fonts/standard/typeface.png",
  "font_smallcaps": "fonts/smallcaps/typeface.png",
  "cursor": "cursor.png",
  "cursor_cell": "cursor-cell.png",
  "cursor_cell1": "cursor-cell1.png",
  "cursor_cell2": "cursor-cell2.png",
  "knight": "knight.png",
  "knight_walk": "knight-walk.png",
  "knight_flinch": "knight-flinch.png",
  "mage": "mage.png",
  "mage_walk": "mage-walk.png",
  "mage_flinch": "mage-flinch.png",
  "floor": "floor.png",
  "pit": "pit.png",
  "wall": "wall.png",
  "wall_base": "wall-base.png",
  "chest": "chest.png",
  "chest_open": "chest-open.png",
  "chest_open1": "chest-open1.png",
  "chest_open2": "chest-open2.png",
  "chest_open3": "chest-open3.png",
  "chest_open4": "chest-open4.png",
  "stairs_up": "stairs-up.png",
  "stairs_down": "stairs-down.png",
  "door": "door.png",
  "door_open": "door-open.png",
  "eye": "eye.png",
  "eye_flinch": "eye-flinch.png",
  "eye_attack": "eye-attack.png",
  "tag_hp": "hp.png",
  "tag_sp": "sp.png",
  "arrow": "arrow.png",
  "bar": "bar.png",
  "bar_small": "bar-small.png",
  "log": "log.png",
  "log_parchment": "log-parchment.png",
  "circle_knight": "circle-knight.png",
  "circle_mage": "circle-mage.png",
  "portrait_knight": "portrait-knight.png",
  "portrait_mage": "portrait-mage.png",
  "portrait_eye": "portrait-eye.png",
  "portrait_enemy": "portrait-enemy.png",
  "portrait_mimic": "portrait-mimic.png",
  "icon_skill": "icon-skill.png",
  "icon_lance": "icon-lance.png",
  "icon_axe": "icon-axe.png",
  "icon_shield": "icon-shield.png",
  "icon_hat": "icon-hat.png",
  "icon_fire": "icon-fire.png",
  "icon_ice": "icon-ice.png",
  "icon_volt": "icon-volt.png",
  "icon_wind": "icon-wind.png",
  "icon_skull": "icon-skull.png",
  "icon_heartplus": "icon-heartplus.png",
  "icon_stairs": "icon-stairs.png",
  "icon_potion": "icon-potion.png",
  "icon_bread": "icon-bread.png",
  "icon_fish": "icon-fish.png",
  "icon_cheese": "icon-cheese.png",
  "icon_emerald": "icon-emerald.png",
  "icon_ankh": "icon-ankh.png",
  "icon_stairs": "icon-stairs.png",
  "skill": "skill.png",
  "box": "box.png",
  "hud": "hud.png",
  "deck": "deck.png",
  "deck_tab": "deck-tab.png",
  "block": "block.png",
  "statusbar": "statusbar.png",
  "fx_impact0": "fx-impact0.png",
  "fx_impact1": "fx-impact1.png",
  "fx_impact2": "fx-impact2.png",
  "fx_impact3": "fx-impact3.png",
  "fx_impact4": "fx-impact4.png",
  "fx_impact5": "fx-impact5.png",
  "fx_impact6": "fx-impact6.png",
  "block_news": "block-news.png",
  "block_sew": "block-sew.png",
  "block_nws": "block-nws.png",
  "block_new": "block-new.png",
  "block_nes": "block-nes.png",
  "block_nef": "block-nef.png",
  "block_sef": "block-sef.png",
  "block_swf": "block-swf.png",
  "block_nwf": "block-nwf.png",
  "block_ne": "block-ne.png",
  "block_se": "block-se.png",
  "block_sw": "block-sw.png",
  "block_nw": "block-nw.png",
  "block_ns": "block-ns.png",
  "block_ew": "block-ew.png",
  "block_n": "block-n.png",
  "block_e": "block-e.png",
  "block_w": "block-w.png",
  "block_s": "block-s.png",
  "block": "block.png"
}

def load():
  global assets
  if assets:
    return assets
  sprites = {}
  fonts = {}
  for name, path in sprite_paths.items():
    try:
      sprites[name] = pygame.image.load(ASSETS_PATH + path).convert_alpha()
    except FileNotFoundError:
      print("FileNotFoundError: Could not find", name, "at", path)
  meta_standard = json.loads(open(ASSETS_PATH + "fonts/standard/metadata.json", "r").read())
  meta_smallcaps = json.loads(open(ASSETS_PATH + "fonts/smallcaps/metadata.json", "r").read())
  fonts["standard"] = Font(sprites["font_standard"], **meta_standard)
  fonts["smallcaps"] = Font(sprites["font_smallcaps"], **meta_smallcaps)
  assets = Assets(sprites, fonts)
