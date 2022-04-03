from config import DEBUG
from time import time_ns

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

def bench(tag, reset=False, print_threshold=0):
  if tag not in benches or reset:
    benches[tag] = time_ns()
    return 0
  else:
    delta = (time_ns() - benches[tag]) / 1e6
    del benches[tag]
    if delta >= print_threshold:
      log(f"{tag} in {delta:.2f}ms")
    return delta

def dictify(obj):
  {key: getattr(obj, key) for key in dir(obj) if (
    key != key.upper()
    and not key.startswith("__")
    and not callable(getattr(obj, key))
  )}
