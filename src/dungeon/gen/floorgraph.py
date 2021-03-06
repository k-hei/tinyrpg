from dataclasses import dataclass, field
from lib.graph import Graph

@dataclass
class FloorGraph(Graph):
  conns: dict = field(default_factory=lambda: {})

  def connections(graph):
    return graph.conns.items()

  def remove(graph, node):
    super().remove(node)
    for n1, n2 in graph.conns:
      if n1 is node or n2 is node:
        del graph.conns[(n1, n2)]

  def connect(graph, node1, node2, *conns):
    edge = (node1, node2)
    graph.edges.append(edge)
    if edge not in graph.conns:
      graph.conns[edge] = conns
    else:
      graph.conns[edge] += conns

  def disconnect(graph, node1, node2=None):
    super().disconnect(node1, node2)
    if node2:
      if (node1, node2) in graph.conns:
        del graph.conns[(node1, node2)]
      if (node2, node1) in graph.conns:
        del graph.conns[(node2, node1)]

  def reconnect(graph, node1, node2, *conns):
    if (node1, node2) in graph.edges:
      graph.conns[(node1, node2)] = conns
    elif (node2, node1) in graph.edges:
      graph.conns[(node2, node1)] = conns
    else:
      graph.connect(node1, node2, *conns)

  def connectors(graph, node1, node2=None):
    connectors = []
    if not node2:
      for (n1, n2), cs in graph.conns.items():
        if n1 is node1 or n2 is node1:
          connectors += cs
    else:
      for edge, cs in graph.conns.items():
        if edge == (node1, node2) or edge == (node2, node1):
          connectors += cs
    return connectors

  def connectees(graph, edge):
    return graph.conns[edge]

  def connector_edge(graph, node, conn):
    return next((e for e, cs in graph.conns.items() if node in e and conn in cs), None)

  def split(graph, conn):
    def flood_fill(graph, node):
      graph.add(node)
      neighbors = graph.neighbors(node)
      neighbors = [n for n, c in neighbors if c is not conn and n not in graph.nodes]
      for neighbor in neighbors:
        flood_fill(graph, neighbor)
    n1, n2 = graph.connectees(conn)
    g1 = flood_fill(n1, FloorGraph())
    if g1.order() == graph.order():
      return None
    g2 = flood_fill(n2, FloorGraph())
    return g1, g2

  def merge(graph1, graph2):
    graph1.nodes += graph2.nodes
    graph1.edges += graph2.edges
    graph1.conns = dict([*graph1.conns.items(), *graph2.conns.items()])
    return graph1
