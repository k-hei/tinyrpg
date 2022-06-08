from town.graph import WorldGraph, WorldLink
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
            (WorldLink(rooms["tutorial1"], "right"), WorldLink(AkimorCentralArea, "left")),
            (WorldLink(AkimorCentralArea, "upper_slope_top"), WorldLink(AkimorCentralArea, "upper_slope_base")),
            (WorldLink(AkimorCentralArea, "lower_slope_top"), WorldLink(AkimorCentralArea, "lower_slope_base")),
            (WorldLink(AkimorCentralArea, "market_doorway"), WorldLink(MarketArea, "entrance")),
            (WorldLink(AkimorCentralArea, "fortune_house_doorway"), WorldLink(FortuneArea, "entrance")),
            (WorldLink(AkimorCentralArea, "chapel_doorway"), WorldLink(TimeChamberArea, "left")),
            (WorldLink(AkimorCentralArea, "blacksmith_doorway"), WorldLink(TimeChamberArea, "right")),
            (WorldLink(AkimorCentralArea, "right"), WorldLink(OutskirtsArea, "left")),
            (WorldLink(OutskirtsArea, "tower"), WorldLink(rooms["shrine"])),
        ],
    )
