from dataclasses import dataclass
from typing import Dict
import json
import pygame
from pygame import Surface, Rect
from text import Font, Ttf

ASSETS_PATH = "assets/"

@dataclass
class Assets:
  sprites: Dict[str, Surface]
  fonts: Dict[str, Font]
  ttf: Dict[str, Ttf]

assets = None
sprite_paths = {
  "cursor": "cursor",
  "cursor_cell": "cursor-cell",
  "cursor_cell1": "cursor-cell1",
  "cursor_cell2": "cursor-cell2",
  "knight": "knight",
  "knight_walk": "knight-walk",
  "knight_down": "knight-down",
  "knight_walkdown": "knight-walkdown",
  "knight_flinch": "knight-flinch",
  "mage": "mage",
  "mage_walk": "mage-walk",
  "mage_down": "mage-down",
  "mage_walkdown": "mage-walkdown",
  "mage_flinch": "mage-flinch",
  "genie": "genie",
  "bubble_talk": "bubble-talk",
  "floor": "floor",
  "pit": "pit",
  "chest": "chest",
  "chest_open": "chest-open",
  "chest_open1": "chest-open1",
  "chest_open2": "chest-open2",
  "chest_open3": "chest-open3",
  "chest_open4": "chest-open4",
  "stairs_up": "stairs-up",
  "stairs_down": "stairs-down",
  "door": "door",
  "door_open": "door-open",
  "eye": "eye",
  "eye_flinch": "eye-flinch",
  "eye_attack": "eye-attack",
  "mushroom": "mushroom",
  "skeleton": "skeleton",
  "hp": "hp",
  "sp_tag": "sp",
  "sp_meter": "sp-meter",
  "sp_fill": "sp-fill",
  "tag_hp": "tag-hp",
  "arrow": "arrow",
  "arrow_dialogue": "arrow-dialogue",
  "bar": "bar",
  "bar_small": "bar-small",
  "log": "log",
  "log_parchment": "log-parchment",
  "circle_knight": "circle-knight",
  "circle_mage": "circle-mage",
  "circ16_knight": "circ16-knight",
  "circ16_mage": "circ16-mage",
  "portrait_knight": "portrait-knight",
  "portrait_mage": "portrait-mage",
  "portrait_enemy": "portrait-enemy",
  "portrait_eyeball": "portrait-eye",
  "portrait_toadstool": "portrait-mushroom",
  "portrait_skeleton": "portrait-skeleton",
  "portrait_mimic": "portrait-mimic",
  "icon_skill": "icon-skill",
  "icon_lance": "icon-lance",
  "icon_axe": "icon-axe",
  "icon_shield": "icon-shield",
  "icon_hat": "icon-hat",
  "icon_fire": "icon-fire",
  "icon_ice": "icon-ice",
  "icon_volt": "icon-volt",
  "icon_wind": "icon-wind",
  "icon_skull": "icon-skull",
  "icon_heartplus": "icon-heartplus",
  "icon_stairs": "icon-stairs",
  "icon_potion": "icon-potion",
  "icon_ankh": "icon-ankh",
  "icon_bread": "icon-bread",
  "icon_fish": "icon-fish",
  "icon_cheese": "icon-cheese",
  "icon_elixir": "icon-elixir",
  "icon_antidote": "icon-antidote",
  "icon_emerald": "icon-emerald",
  "icon_balloon": "icon-balloon",
  "icon_stairs": "icon-stairs",
  "skill": "skill",
  "box": "box",
  "hud": "hud",
  "hud_town": "hud-town",
  "belt": "item-belt",
  "item_text": "item-text",
  "item_tiles": "item-tiles",
  "item_desc": "item-desc",
  "hand": "hand",
  "deck": "deck",
  "deck_tab": "deck-tab",
  "statusbar": "statusbar",
  "fx_impact0": "fx-impact0",
  "fx_impact1": "fx-impact1",
  "fx_impact2": "fx-impact2",
  "fx_impact3": "fx-impact3",
  "fx_impact4": "fx-impact4",
  "fx_impact5": "fx-impact5",
  "fx_impact6": "fx-impact6",
  "fx_burst0": "burst0",
  "fx_burst1": "burst1",
  "fx_burst2": "burst2",
  "fx_burst3": "burst3",
  "fx_burst4": "burst4",
  "fx_spark0": "spark0",
  "fx_spark1": "spark1",
  "fx_spark2": "spark2",
  "fx_spark3": "spark3",
  "fx_smallspark0": "spark1",
  "fx_smallspark1": "spark2",
  "fx_smallspark2": "spark3",
  "soul0": "soul0",
  "soul1": "soul1",
  "soul2": "soul2",
  "soul3": "soul3",
  "soul4": "soul4",
  "block_news": "block-news",
  "block_ews": "block-ews",
  "block_nws": "block-nws",
  "block_new": "block-new",
  "block_nes": "block-nes",
  "block_nef": "block-nef",
  "block_sef": "block-sef",
  "block_swf": "block-swf",
  "block_nwf": "block-nwf",
  "block_ne": "block-ne",
  "block_se": "block-se",
  "block_sw": "block-sw",
  "block_nw": "block-nw",
  "block_ns": "block-ns",
  "block_ew": "block-ew",
  "block_n": "block-n",
  "block_e": "block-e",
  "block_w": "block-w",
  "block_s": "block-s",
  "block": "block",
  "wall_base": "wall-base",
  "wall_edge": "wall-edge",
  "wall_link": "wall-link",
  "wall_torch": "wall-torch",
  "town": "town",
  "tower": "tower"
}

def load_font(font_name):
  typeface = pygame.image.load(ASSETS_PATH + "fonts/" + font_name + "/typeface.png").convert_alpha()
  metadata = json.loads(open(ASSETS_PATH + "fonts/" + font_name + "/metadata.json", "r").read())
  return Font(typeface, **metadata)

def load_ttf(font_name):
  font = pygame.font.Font(ASSETS_PATH + "ttf/" + font_name + ".ttf", 8)
  return Ttf(font)

def load():
  global assets
  if assets:
    return assets
  sprites = {}
  fonts = {}
  ttf = {}
  for name, path in sprite_paths.items():
    try:
      sprite = pygame.image.load(ASSETS_PATH + path + ".png").convert_alpha()
    except FileNotFoundError:
      sprite = None
      print("FileNotFoundError: Could not find", name, "at", path)
    try:
      metadata = json.loads(open(ASSETS_PATH + path + ".json", "r").read())
    except FileNotFoundError:
      metadata = None
    if sprite and metadata:
      for name, rect in metadata.items():
        sprites[name] = sprite.subsurface(Rect(*rect))
    elif sprite:
      sprites[name] = sprite
  fonts["standard"] = load_font("standard")
  fonts["smallcaps"] = load_font("smallcaps")
  fonts["numbers13"] = load_font("numbers13")
  fonts["numbers16"] = load_font("numbers16")
  fonts["english"] = load_font("english")
  ttf["english"] = load_ttf("PCPaintEnglishSmall")
  ttf["roman"] = load_ttf("PCPaintRomanSmall")
  assets = Assets(sprites, fonts, ttf)
