from town.graph import WorldGraph
from town.areas.akimor_central import AkimorCentralArea
from town.areas.fortune import FortuneArea
from town.areas.store import StoreArea as MarketArea
from town.areas.outskirts import OutskirtsArea
from town.areas.time_chamber import TimeChamberArea
from contexts.explore.roomdata import rooms


def construct_world():
    return WorldGraph(
        nodes=[rooms["tutorial1"], AkimorCentralArea, FortuneArea, MarketArea, OutskirtsArea, TimeChamberArea],
        edges=[
            ((rooms["tutorial1"], "right"), (AkimorCentralArea, "left")),
            ((AkimorCentralArea, "upper_slope_top"), (AkimorCentralArea, "upper_slope_base")),
            ((AkimorCentralArea, "lower_slope_top"), (AkimorCentralArea, "lower_slope_base")),
            ((AkimorCentralArea, "market_doorway"), (MarketArea, "entrance")),
            ((AkimorCentralArea, "fortune_house_doorway"), (FortuneArea, "entrance")),
            ((AkimorCentralArea, "chapel_doorway"), (TimeChamberArea, "left")),
            ((AkimorCentralArea, "blacksmith_doorway"), (TimeChamberArea, "right")),
            ((AkimorCentralArea, "right"), (OutskirtsArea, "left")),
        ],
    )
