from dataclasses import dataclass


@dataclass(frozen=True)
class ElementData:
    name: str
    image_id: str
    tile_id: int = -1
    layer: str = "elems"
    size: tuple[int, int] = (1, 1)
    offset: tuple[int, int] = (0, 0)
    hitbox: tuple[int, int, int, int] = None
