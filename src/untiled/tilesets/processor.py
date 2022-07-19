import json


def load_json(json_path):
    with open(json_path, mode="r", encoding="utf-8") as json_file:
        return json.loads(json_file.read())


class Processor:

    @classmethod
    def load_metadata(cls, metadata):
        pass

    @staticmethod
    def process_image_layer(layer, image):
        pass

    @staticmethod
    def process_tile_layer(layer, image):
        pass

    @staticmethod
    def process_object_layer(layer, image):
        pass

    @staticmethod
    def process_trigger_layer(layer, image):
        pass
