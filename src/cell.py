def manhattan(a, b):
  return abs(b[0] - a[0]) + abs(b[1] - a[1])

def is_adjacent(a, b):
  return manhattan(a, b) == 1

def add(a, b):
  return (a[0] + b[0], a[1] + b[1])

def is_odd(cell):
  return cell[0] % 2 == 1 and cell[1] % 2 == 1
