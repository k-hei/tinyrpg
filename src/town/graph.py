from abc import ABC, abstractmethod
from dataclasses import dataclass
from lib.graph import Graph


class WorldNode(ABC):
    """
    A blueprint that defines an area in the game world.
    Instantiated nodes should ideally be invalid to avoid ref divergence on clone.
    """

class WorldPort:
    """
    Models a port in the game world.
    A port defines the location and direction of incoming spawns and outgoing connections.
    """
    x: int = None
    y: int = None
    direction: tuple[int, int] = (0, 0)

@dataclass
class WorldLink:
    """
    Models a link in the game world.
    A link is a uniquely identifiable port.
    As raw data, standard ports are unable to uniquely identify themselves, and require a node to be
    specified for contextualization purposes.
    """
    node: WorldNode
    port_id: str

    def __hash__(link):
        return hash(link.node) * hash(link.port_id)

    @property
    def port(link):
        return link.node.ports[link.port_id]


class WorldGraph(Graph):

    def tail(graph, link):
        for n1, n2 in graph.edges:
            if n1 == link:
                return n2
            if n2 == link:
                return n1
