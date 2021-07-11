from contexts.app import App
from contexts.loading import LoadingContext

App(
  title="loading screen demo",
  context=LoadingContext()
).init()
