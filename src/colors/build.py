import __init__ as colors

if __name__ == "__main__":
  color_names = [n for n in dir(colors) if n != n.lower()]
  hex_map = {n: getattr(colors, n) for n in color_names}
  rgb_map = {n: colors.rgbify(hex_map[n]) for n in color_names}
  buffer = ""
  for color_name, color_value in rgb_map.items():
    buffer += "{name} = {value}\n".format(name=color_name, value=color_value)
  output_file = open("src/colors/palette.py", "w")
  output_file.write(buffer)
  output_file.close()
