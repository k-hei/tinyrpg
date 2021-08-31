from town.sideview.stage import Area, AreaLink
from town.sideview.actor import Actor
from cores.rat import Rat
from cores.radhead import Radhead
from cores.beetless import Beetless
from config import TILE_SIZE
from contexts.prompt import PromptContext, Choice
from items.materials.beetle import Beetle
from items.sp.berry import Berry

class ClearingArea(Area):
  name = "Alleyway"
  bg = "town_clearing"
  links = {
    "alley": AreaLink(x=96, direction=(0, 1)),
  }

  def init(area, town):
    super().init(town)
    area.spawn(Actor(core=Rat(
      name=(rat_name := "Rascal"),
      facing=(-1, 0),
      message=lambda town: [
        (rat_name, "Hmmm?"),
        (rat_name, "I haven't seen you around before. You new here?")
      ]),
    ), x=32)

    BUGHEAD_NAME = "Beetless"
    SIDEKICK_NAME = "Radhead"
    BUGHEAD_MESSAGE = lambda town: (
      town.store.is_quest_completed("fetch_beetles") and [
        (BUGHEAD_NAME, "Oh, it's you, heh heh. Got any more beetles for me?"),
        (BUGHEAD_NAME, "If you find me any more, I'll get you something good."),
      ] or town.store.is_quest_accepted("fetch_beetles") and Beetle in town.store.items and [
        (BUGHEAD_NAME, "Find any beetles yet?"),
        PromptContext(
          message=("Give {} the ".format(BUGHEAD_NAME.upper()), Beetle().token(), "?"),
          choices=[
            Choice("Yes"),
            Choice("No", closing=True)
          ],
          on_close=lambda choice: (
            choice.text == "Yes" and [
              (BUGHEAD_NAME, "Woah! Heh heh... Cool!"),
              (SIDEKICK_NAME, "He brought you back a fat one, {}. Time to pay up!".format(BUGHEAD_NAME)),
              (BUGHEAD_NAME, "heh heh. Oh yeah. Hold on."),
              (BUGHEAD_NAME, ("You can have this ", Berry().token(), " I found in the outskirts.")),
              (BUGHEAD_NAME, "It looks kinda cool, heh heh."),
              ("", ("Got ", Berry().token(), "!")),
              town.store.obtain(Berry),
              town.store.complete_quest("fetch_beetles"),
            ] or choice.text == "No" and []
          )
        )
      ] or town.store.is_quest_accepted("fetch_beetles") and [
        (BUGHEAD_NAME, "Find any beetles yet?"),
        (BUGHEAD_NAME, "They usually hang out in like, the tombs and stuff."),
        (BUGHEAD_NAME, "If you find me one, I'll give you something cool."),
      ] or [
        (BUGHEAD_NAME, "So like, I'm a great big fan of bugs."),
        (SIDEKICK_NAME, "Heh heh... You're only a fan of beetles, {}.".format(BUGHEAD_NAME)),
        (BUGHEAD_NAME, "Heh... oh yeah. Well, anyways... I really like beetles."),
        (BUGHEAD_NAME, "If you can find any, I'll give them a good home and you can have like,"),
        (BUGHEAD_NAME, "a reward or something."),
        (BUGHEAD_NAME, "They usually hang out in like, the tombs and stuff."),
        (BUGHEAD_NAME, "They're sensitive though, so you have to sneak up on 'em."),
        (SIDEKICK_NAME, "If you bring back a fat one, he'll give you three million dollars."),
        (BUGHEAD_NAME, "Shut up! No I won't! I'm poor. Heh."),
        (BUGHEAD_NAME, "But I'll give you something for your troubles."),
        (BUGHEAD_NAME, "I don't know what yet, I have to check my house for stuff I'm not using."),
        (BUGHEAD_NAME, "Anyways, if you find any beetles in the tombs, I'll give you something cool."),
        town.store.accept_quest("fetch_beetles")
      ]
    )
    area.spawn(Actor(core=Beetless(
      name=BUGHEAD_NAME,
      message=BUGHEAD_MESSAGE
    )), x=192)
    area.spawn(Actor(core=Radhead(
      name=SIDEKICK_NAME,
      message=BUGHEAD_MESSAGE,
      facing=(-1, 0)
    )), x=224)
