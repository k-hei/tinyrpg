from lib.graph import Graph

class FloorGraph(Graph):
  def __init__(graph):
    super().__init__()
    graph.conns = {}

  def connect(graph, node1, node2, conn):
    edge = (node1, node2)
    graph.edges.append(edge)
    if edge not in graph.conns:
      graph.conns[edge] = [conn]
    else:
      graph.conns[edge].append(conn)

  def disconnect(graph, node1, node2=None):
    super().disconnect(node1, node2)
    if node2:
      if (node1, node2) in graph.conns:
        del graph.conns[(node1, node2)]
      if (node2, node1) in graph.conns:
        del graph.conns[(node2, node1)]

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

  def connectees(graph, conn):
    return graph.conns[conn]

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
