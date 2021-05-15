from pygame import Surface, SRCALPHA
from contexts import Context
from assets import load as use_assets
from palette import WHITE

SPACING_FACTOR = 2
TITLE_SPACING = 16

class NameEntryContext(Context):
  def __init__(ctx, default_name=""):
    ctx.name = default_name
    ctx.matrix = (
      "ABCDE abcde",
      "FGHIJ fghij",
      "KLMNO klmno",
      "PQRST pqrst",
      "UVWXY uvwxy",
      "Z     z"
    )

  def draw(ctx, surface):
    assets = use_assets()
    font = assets.ttf["roman"]
    char_size = font.get_size() * SPACING_FACTOR
    cols = len(ctx.matrix[0])
    rows = len(ctx.matrix)

    title_surface = font.render("Please enter a name.")
    x = surface.get_width() // 2 - title_surface.get_width() // 2
    y = 32
    surface.blit(title_surface, (x, y))

    name_surface = font.render("- - - - - -")
    x = surface.get_width() // 2 - name_surface.get_width() // 2
    y = 56
    surface.blit(name_surface, (x, y))

    char_surface = Surface((cols * char_size, rows * char_size), SRCALPHA)
    for row, line in enumerate(ctx.matrix):
      for col, char in enumerate(line):
        image = font.render(char, WHITE)
        x = col * char_size
        y = row * char_size
        char_surface.blit(image, (x, y))
    x = surface.get_width() // 2 - char_surface.get_width() // 2
    y = surface.get_height() // 2 - char_surface.get_height() // 2 + 16
    surface.blit(char_surface, (x, y))
