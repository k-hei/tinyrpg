from lib.cell import add as add_vector
from skills.weapon.broadsword import BroadSword
from contexts.cutscene import CutsceneContext
from contexts.dialogue import DialogueContext
from anims.flicker import FlickerAnim
from anims.jump import JumpAnim
from anims.pause import PauseAnim
from anims.shake import ShakeAnim
import config

def on_defeat(room, game, actor):
  if actor is not room.mage:
    return True
  if "minxia" not in game.store.story:
    game.store.story.append("minxia")
  game.anims.append([PauseAnim(
    duration=30,
    on_end=lambda: game.open(CutsceneContext(
      script=[
        *postbattle_cutscene_setup(room, game),
        *(postbattle_cutscene(room, game) if config.CUTSCENES else []),
        *postbattle_cutscene_teardown(room, game),
        lambda step: (
          room.unlock(game),
          step()
        )
      ]
    ))
  )])
  return False

def postbattle_cutscene_setup(room, game):
  mage = room.mage
  return [
    lambda step: (
      mage.revive(hp_factor=0),
      enemies := [e for e in room.get_enemies(game.floor) if e is not mage],
      game.anims.extend([
        [(lambda e: FlickerAnim(
          target=e,
          duration=45,
          on_end=lambda: game.floor.remove_elem(e)
        ))(e) for e in enemies],
        [PauseAnim(duration=15, on_end=step)]
      ]) if enemies else step()
    )
  ]

def postbattle_cutscene(room, game):
  knight = game.hero
  mage = room.mage
  midpoint = (
    (knight.cell[0] + mage.cell[0]) / 2,
    (knight.cell[1] + mage.cell[1]) / 2
  )
  return [
    lambda step: (
      setattr(mage, "faction", "ally"),
      game.camera.focus(midpoint, speed=8, force=True),
      mage.face(knight.cell),
      game.anims.append([JumpAnim(target=mage, on_end=step)])
    ),
    lambda step: game.child.open(DialogueContext(script=[
      (mage.name, "OKAY OKAY! Alright. I get it now. I'll come along."),
      (mage.name, "I obviously can't get rid of you, so I submit."),
      lambda: knight.face(mage.cell),
      (knight.name, "I don't have anything to tie you up with,"),
      (knight.name, "so I'm trusting you not to run away."),
    ]), on_close=step),
    lambda step: game.anims.append([ShakeAnim(target=mage, duration=30, on_end=step)]),
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
    lambda step: game.child.open(DialogueContext(script=[
      (mage.name, "Boy are you dumb! But I don't think I will."),
      (mage.name, "My spirit is crushed. I am depressed."),
    ]), on_close=step),
    lambda step: (
      game.camera.focus(add_vector(room.get_edges()[0], (0, 2)), speed=8, force=True),
      game.anims.append([PauseAnim(duration=15, on_end=step)]),
    ),
    lambda step: (
      knight.face(add_vector(knight.cell, (0, -1))),
      step()
    ),
    lambda step: game.child.open(DialogueContext(script=[
      (knight.name, "Now to find a way out of here..."),
      (mage.name, "I am so depressed..."),
    ]), on_close=step),
  ]

def postbattle_cutscene_teardown(room, game):
  mage = room.mage
  return [
    lambda step: (
      game.recruit(mage),
      room.unlock(game),
      game.learn_skill(skill=BroadSword),
      game.end_step(),
      step()
    ),
    lambda step: game.child.open(DialogueContext(
      script=[
        ("", ("Received ", BroadSword().token(), ".")),
      ],
      log=game.log
    ), on_close=step),
  ]
