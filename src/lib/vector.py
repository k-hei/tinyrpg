def add(*vectors):
  c = []
  for i in range(max(*[len(v) for v in vectors])):
    x = 0
    for v in vectors:
      x += v[i]
    c.append(x)
  return tuple(c)

def subtract(*vectors):
  if len(vectors) == 1:
    return vectors[0]
  c = []
  for i in range(max(*[len(v) for v in vectors])):
    x = vectors[0][i]
    for v in vectors[1:]:
      x -= v[i]
    c.append(x)
  return tuple(c)

def negate(vector):
  return subtract(tuple([0] * len(vector)), vector)

def scale(vector, scalar):
  return tuple([v * scalar for v in vector])
