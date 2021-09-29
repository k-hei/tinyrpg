from comps.log import Token
from colors.palette import GREEN

def on_enter(room, game):
  genie = game.floor.find_elem(cls="Genie")
  genie.core.message = [
    (genie.name, ("Congratulations, ", game.hero.token(), "!")),
    (genie.name, "You've completed all the story content for this demo."),
    (genie.name, "However, your journey has only just begun."),
    (genie.name, "What other secrets lie hidden within the tomb?"),
    ("", ("(You've unlocked the ", Token(text="infinite dungeon", color=GREEN), "!)")),
    ("", "(Re-enter the tomb from the town and explore the new path that's opened up.)"),
  ]
