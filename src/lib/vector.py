def add(*vectors):
  c = []
  for i in range(max(*[len(v) for v in vectors])):
    x = 0
    for v in vectors:
      x += v[i]
    c.append(x)
  return tuple(c)

def scale(vector, scalar):
  return tuple([v * scalar for v in vector])
