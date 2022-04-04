from dataclasses import dataclass


@dataclass(frozen=True)
class ElementData:
    name: str
    image_id: str
    tile_id: int = -1
    size: tuple[int, int] = (1, 1)
    hitbox: tuple[int, int, int, int] = (-8, -16, 16, 16)
