from contexts.app import App
from contexts.load import LoadContext

App(title="load data demo", context=LoadContext()).init()
