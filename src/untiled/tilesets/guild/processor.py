from os.path import join
from PIL import Image
from untiled.tilesets.processor import Processor


class GuildProcessor(Processor):
    cwd = ""

    @classmethod
    def load_metadata(cls, metadata):
        cls.cwd = metadata["cwd"]

    @classmethod
    def process_image_layer(cls, layer, image):
        image_path = layer["image"]
        image_path = join(cls.cwd, image_path)
        image = Image.open(image_path)
        return image

    @staticmethod
    def process_object_layer(layer, image):
        elems = []
        tiles = []
        return image, elems, tiles
