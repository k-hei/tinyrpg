from town.graph import WorldGraph
from town.areas.akimor_central import AkimorCentralArea
from contexts.explore.roomdata import rooms


def construct_world():
    return WorldGraph(
      nodes=[rooms["tutorial1"], AkimorCentralArea],
      edges=[
        ((rooms["tutorial1"], "right"), (AkimorCentralArea, "left")),
      ],
    )
