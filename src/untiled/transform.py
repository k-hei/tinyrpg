from PIL import Image, ImageOps


MASK_HORIZ = 0x80000000
MASK_VERT = 0x40000000
MASK_DIAG = 0x20000000

transform_map = {
    MASK_HORIZ + MASK_VERT + MASK_DIAG: lambda image: (
        ImageOps.mirror(image).transpose(Image.ROTATE_90)
    ),
    MASK_HORIZ + MASK_VERT: lambda image: (
        image.transpose(Image.ROTATE_180)
    ),
    MASK_HORIZ + MASK_DIAG: lambda image: (
        image.transpose(Image.ROTATE_270)
    ),
    MASK_HORIZ: lambda image: (
        image.transpose(Image.FLIP_LEFT_RIGHT)
    ),
    MASK_VERT + MASK_DIAG: lambda image: (
        image.transpose(Image.ROTATE_90)
    ),
    MASK_VERT: lambda image: (
        image.transpose(Image.FLIP_TOP_BOTTOM)
    ),
    MASK_DIAG: lambda image: (
        image.transpose(Image.TRANSVERSE).transpose(Image.ROTATE_180)
    ),
    0: lambda image: image,
}

def transform_image(image, mask):
    return transform_map[mask](image)

def extract_transform_mask(tile):
    mask = tile & 0xff000000
    if mask:
        tile &= 0x00ffffff
    return tile, mask
