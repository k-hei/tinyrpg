from config import DEBUG
from pygame.time import get_ticks

buffer = ""
benches = {}

def log(*args):
  if DEBUG:
    print("[DEBUG]", *args)

def append(text):
  global buffer
  if not buffer.endswith(text):
    buffer += text
    log(text)

def write():
  if not buffer:
    return
  debug_file = open("debug.log", "w")
  debug_file.write(buffer)
  debug_file.close()

def bench(tag, quiet=False):
  if tag not in benches:
    benches[tag] = get_ticks()
    return 0
  else:
    diff = get_ticks() - benches[tag]
    del benches[tag]
    if not quiet:
      log("{} in {}ms".format(tag, diff))
    return diff

def dictify(obj):
  {key: getattr(obj, key) for key in dir(obj) if (
    key != key.upper()
    and not key.startswith("__")
    and not callable(getattr(obj, key))
  )}
