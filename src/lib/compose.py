def compose(parent_fn, child_fn):
  return lambda *args: (
    parent_fn and parent_fn(*args),
    child_fn and child_fn(*args),
  )
