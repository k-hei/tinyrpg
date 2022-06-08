from math import sqrt
from lib.lerp import lerp as _lerp

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

def multiply(*vectors):
  if len(vectors) == 1:
    return vectors[0]
  c = []
  for i in range(max(*[len(v) for v in vectors])):
    x = vectors[0][i]
    for v in vectors[1:]:
      x *= v[i]
    c.append(x)
  return tuple(c)

def scale(vector, scalar):
  return tuple([v * scalar for v in vector])

def lerp(a, b, t):
  c = []
  for i in range(max(len(a), len(b))):
    c.append(_lerp(a[i], b[i], t))
  return c

def mean(*vectors):
  if len(vectors) == 1:
    return vectors[0]
  c = []
  for i in range(max(*[len(v) for v in vectors])):
    s = 0
    for v in vectors:
      s += v[i]
    c.append(s / len(vectors))
  return tuple(c)

def floor(vector):
  return tuple([int(x) for x in vector])

_round = round
def round(vector):
  return tuple([_round(x) for x in vector])

def distance(a, b):
  x1, y1 = a
  x2, y2 = b
  dx, dy = x2 - x1, y2 - y1
  return sqrt(dx * dx + dy * dy)

def normalize(vector):
  dist = sqrt(vector[0] * vector[0] + vector[1] * vector[1])
  return (
    vector[0] / dist,
    vector[1] / dist,
  )

def tangent(vector):
  x, y = vector
  return (-y, x)
