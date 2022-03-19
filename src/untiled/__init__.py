import base64
import zstd


def decode(width, height, layers, **kwargs):
    layers_data = decode_layers(layers)
    return layers_data

def decode_layers(layers):
    return {layer["name"]: decode_layer(**layer)
        for layer in layers if layer["type"] == "tilelayer"}

def decode_layer(width, height, data, **kwargs):
    data_bytes = zstd.loads(base64.b64decode(data))
    data_ids = [decode_byte(buffer=data_bytes, address=i) for i in range(0, len(data_bytes), 4)]
    data_size = len(data_ids)
    data_lines = [data_ids[i:i+width] for i in range(0, data_size, width)]
    return data_lines

def decode_byte(buffer, address):
    BYTE_SIZE = 2 ** 8
    return (buffer[address] - 1
        + buffer[address + 1] * BYTE_SIZE ** 1
        + buffer[address + 2] * BYTE_SIZE ** 2
        + buffer[address + 3] * BYTE_SIZE ** 3)


class TilesetProcessor:

    @staticmethod
    def get_layer_dimensions(layer):
        return (len(layer[0]), len(layer))

    @classmethod
    def process(cls, layer, image=None):
        pass
