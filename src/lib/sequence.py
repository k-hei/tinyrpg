sequence_stops = []

def play_sequence(sequence, on_end=None):
  index = -1
  interrupt = False

  def step():
    nonlocal index
    index = (index + 1) % len(sequence)
    not interrupt and sequence[index](step)

  def stop():
    nonlocal interrupt
    interrupt = True

  step()
  sequence_stops.append((sequence, stop))

def stop_sequence(sequence):
  stop = next((s for q, s in sequence_stops if q is sequence), None)
  if stop:
    stop()
    sequence_stops.remove((sequence, stop))
