from town.sideview.stage import Area, AreaLink
from town.sideview.actor import Actor
from cores.rat import Rat
from cores.radhead import Radhead
from cores.beetless import Beetless
from config import TILE_SIZE

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
      message=lambda town: [
        (rat_name, "Fuck you")
      ])
    ), x=192)

    BUGHEAD_NAME = "Beetless"
    SIDEKICK_NAME = "Radhead"
    BUGHEAD_SCRIPT = [
      (BUGHEAD_NAME, "So like, I'm a great big fan of bugs."),
      (SIDEKICK_NAME, "Heh heh... You're only a fan of beetles, BEETLESS."),
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
    ]
    area.spawn(Actor(core=Beetless(
      name=(bughead_name := "Beetless"),
      message=lambda town: BUGHEAD_SCRIPT
    )), x=64)
    area.spawn(Actor(core=Radhead(
      name=(sidekick_name := "Radhead"),
      message=lambda town: BUGHEAD_SCRIPT
    )), x=32)
