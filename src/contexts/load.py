from os import path
import pygame
import lib.keyboard as keyboard
from contexts.data import DataContext
from contexts.dialogue import DialogueContext
from contexts.prompt import PromptContext, Choice
from contexts.controls import ControlsContext
from transits.dissolve import DissolveIn, DissolveOut
from game.data import GameData

import assets
from lib.sprite import Sprite
from lib.filters import outline
from colors.palette import BLACK
from config import WINDOW_WIDTH, ROOT_PATH


class LoadContext(DataContext):
  TITLE = "LOAD DATA"
  ACTION = "Load"
  EXTRA_CONTROLS = {}

  def enter(ctx):
    super().enter()
    ctx.version = None

    ctx.can_close = type(ctx.parent).__name__ not in ("AppContext", "GameContext")
    if not ctx.can_close:
      ctx.EXTRA_CONTROLS = { "esc": "Controls" }
      ctx.version = "STAGING"
      try:
        with open(path.join(ROOT_PATH, "VERSION"), mode="r", encoding="utf-8") as version_file:
          ctx.version = version_file.read().rstrip()
      except FileNotFoundError:
        pass

    ctx.anims[-1].on_end = lambda: ctx.open(
      DialogueContext(script=["Please select a file to load."], lite=True)
    )

  def handle_press(ctx, button):
    if super().handle_press(button) != None:
      return False

    if not ctx.can_close and not ctx.hidden and button == pygame.K_ESCAPE and keyboard.get_state(button) == 1:
      ctx.handle_controls()

  def handle_controls(ctx):
    ctx.hide(on_end=lambda: ctx.open(ControlsContext(), on_close=ctx.show))

  def handle_action(ctx):
    savedata = ctx.slots[ctx.index].data
    if savedata is None:
      return False
    ctx.open(PromptContext("Load this file?", [
      Choice("Yes"),
      Choice("No", closing=True)
    ], on_close=lambda choice:
      choice and choice.text == "Yes" and ctx.open(DialogueContext(
        script=["Save data loaded successfully."],
        lite=True,
        on_close=lambda: ctx.get_head().transition([
          DissolveIn(on_end=lambda: ctx.close(savedata)),
          DissolveOut()
        ])
      ))
    ))

  def view(ctx, *args, **kwargs):
    sprites = super().view(*args, **kwargs)

    if ctx.version:
      try:
        version_image = ctx.__version_image
      except AttributeError:
        version_text = ctx.version
        version_image = assets.ttf["normal"].render(text=version_text)
        version_image = outline(version_image, BLACK)
        ctx.__version_image = version_image

      sprites += [Sprite(
        image=version_image,
        pos=(WINDOW_WIDTH, 0),
        origin=Sprite.ORIGIN_TOPRIGHT,
        layer="ui",
      )]

    return sprites
