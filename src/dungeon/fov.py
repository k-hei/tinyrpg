import math

def get_projection(row, col):
  start = col / (row + 2)
  end = (col + 1) / (row + 1)
  return (start, end)

def transform_octant(row, col, octant):
  if octant == 0: return (col, -row)
  if octant == 1: return (row, -col)
  if octant == 2: return (row, col)
  if octant == 3: return (col, row)
  if octant == 4: return (-col, row)
  if octant == 5: return (-row, col)
  if octant == 6: return (-row, -col)
  if octant == 7: return (-col, -row)

def cast_octant(stage, start, vision, octant):
  cells = []
  shadows = []
  shadowed = False
  start_x, start_y = start
  for row in range(1, int(vision + 1)):
    transf_x, transf_y = transform_octant(row, 0, octant)
    cell = (start_x + transf_x, start_y + transf_y)
    if not stage.contains(cell):
      break
    for col in range(row + 1):
      transf_x, transf_y = transform_octant(row, col, octant)
      cell = (start_x + transf_x, start_y + transf_y)
      if not stage.contains(cell) or transf_x * transf_x + transf_y * transf_y > vision * vision:
        break
      if shadowed:
        continue
      proj_start, proj_end = get_projection(row, col)
      def does_shadow_cover_proj(shadow):
        shadow_start, shadow_end = shadow
        return shadow_start <= proj_start and shadow_end >= proj_end
      visible = next((shadow for shadow in shadows if does_shadow_cover_proj(shadow)), None) is None
      if not visible:
        continue
      cells.append(cell)
      if not stage.is_cell_opaque(cell):
        continue
      index = 0
      while index < len(shadows):
        shadow_start, _ = shadows[index]
        if shadow_start >= proj_start:
          break
        index += 1
      prev_start, prev_end = shadows[index - 1] if index > 0 else (None, None)
      next_start, next_end = shadows[index] if index < len(shadows) else (None, None)
      over_prev = index > 0 and prev_end > proj_start
      over_next = index < len(shadows) and next_start < proj_end
      if over_next:
        if over_prev:
          shadows[index - 1] = (prev_start, next_end)
          shadows.pop(index)
        else:
          shadows[index] = (proj_start, next_end)
      else:
        if over_prev:
          shadows[index - 1] = (prev_start, proj_end)
        else:
          shadows.insert(index, (proj_start, proj_end))
      if len(shadows) == 1:
        shadow_start, shadow_end = shadows[0]
        shadowed = shadow_start == 0 and shadow_end == 1
  return cells

def shadowcast(stage, start, vision):
  cells = []
  for i in range(8):
    cells += cast_octant(stage, start, vision, i)
  cells.append(start)
  return cells
