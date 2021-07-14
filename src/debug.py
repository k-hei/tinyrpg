from config import DEBUG

buffer = ""

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
