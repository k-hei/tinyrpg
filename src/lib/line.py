def connect_lines(points, closed=False):
  if len(points) < 2:
    return []

  lines = []
  for i, point in enumerate(points[1:]):
    lines.append((points[i], point))

  if closed:
    lines.append((points[-1], points[0]))

  return lines

def find_lines_intersection(line1, line2):
  a, b = line1
  c, d = line2

  p0_x, p0_y = a
  p1_x, p1_y = b
  p2_x, p2_y = c
  p3_x, p3_y = d

  s1_x = p1_x - p0_x
  s1_y = p1_y - p0_y
  s2_x = p3_x - p2_x
  s2_y = p3_y - p2_y

  d = -s2_x * s1_y + s1_x * s2_y
  if d == 0:
    return None

  s = (-s1_y * (p0_x - p2_x) + s1_x * (p0_y - p2_y)) / d
  t = (s2_x * (p0_y - p2_y) - s2_y * (p0_x - p2_x)) / d

  return (
    p0_x + (t * s1_x), p0_y + (t * s1_y)
  ) if 0 <= s <= 1 and 0 <= t <= 1 else None

def find_slope(line):
  dist_x = line[1][0] - line[0][0]
  dist_y = line[0][1] - line[1][1]
  return dist_y / (dist_x or 1)
