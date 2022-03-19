import base64
import zstd


def decode_layers(layers):
    layers_data = [decode_layer(**layer) for layer in layers if layer["type"] == "tilelayer"]
    return layers_data

def decode(width, height, layers, **kwargs):
    layers_data = decode_layers(layers)
    return layers_data

def decode_layer(width, height, data, **kwargs):
    data_bytes = zstd.loads(base64.b64decode(data))
    print(data_bytes)
    data_ids = [
        data_bytes[i] + data_bytes[i + 1] * 256 + data_bytes[i + 2] * 256 * 256 + data_bytes[i + 3] * 256 * 256 * 256 - 1
                for i in range(0, len(data_bytes), 4)]
    data_size = len(data_ids)
    data_lines = [data_ids[i:i+width] for i in range(0, data_size, width)]
    return data_lines


class TilesetProcessor:

    @staticmethod
    def get_layer_dimensions(layer):
        return (len(layer[0]), len(layer))

    @classmethod
    def process(cls, layer):
        pass
