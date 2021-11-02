from pygame import Surface, Rect, SRCALPHA
from pygame.draw import rect as draw_rect
import assets
from colors.palette import BLACK, WHITE

TAG_XPADDING = 3
TAG_YPADDING = 3

class ShopTag:
  def __init__(tag, content_spriteid):
    tag.content_spriteid = content_spriteid

  def render(tag):
    content_image = assets.sprites[tag.content_spriteid]
    tag_width = (
      assets.sprites["shop_tag_l"].get_width()
      + content_image.get_width()
      + TAG_XPADDING * 2
      + assets.sprites["shop_tag_r"].get_width()
    )
    tag_height = assets.sprites["shop_tag_l"].get_height()
    tag_surface = Surface((tag_width, tag_height), flags=SRCALPHA)
    tag_surface.blit(assets.sprites["shop_tag_l"], (0, 0))
    tag_surface.blit(assets.sprites["shop_tag_r"],
      (tag_width - assets.sprites["shop_tag_r"].get_width(), 0))
    draw_rect(tag_surface, WHITE, Rect(
      (assets.sprites["shop_tag_l"].get_width(), 0),
      (content_image.get_width() + TAG_XPADDING * 2, tag_height)
    ))
    draw_rect(tag_surface, BLACK, Rect(
      (assets.sprites["shop_tag_l"].get_width(), 1),
      (content_image.get_width() + TAG_XPADDING * 2, tag_height - 2)
    ))
    tag_surface.blit(content_image,
      (assets.sprites["shop_tag_l"].get_width() + TAG_XPADDING, TAG_YPADDING))
    return tag_surface
