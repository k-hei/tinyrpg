def compose(parent_fn, child_fn):
  return lambda: (
    parent_fn and parent_fn(),
    child_fn()
  )
