class FloorGraph:
  def __init__(graph):
    graph.nodes = []
    graph.edges = []
    graph.conns = {}

  def order(graph):
    return len(graph.nodes)

  def size(graph):
    return len(graph.edges)

  def degree(graph, node):
    return len(graph.neighbors(node))

  def add(graph, node):
    graph.nodes.append(node)

  def remove(graph, node):
    for neighbor in graph.neighbors(node):
      graph.disconnect(node, neighbor)
    graph.nodes.remove(node)

  def neighbors(graph, node):
    neighbors = set()
    for n1, n2 in graph.edges:
      if n1 is node:
        neighbors.add(n2)
      elif n2 is node:
        neighbors.add(n1)
    return tuple(neighbors)

  def connectors(graph, node1, node2):
    connectors = []
    for edge, cs in graph.conns.items():
      if edge == (node1, node2) or edge == (node2, node1):
        connectors += cs
    return connectors

  def connectees(graph, conn):
    return graph.conns[conn]

  def connect(graph, node1, node2, conn):
    edge = (node1, node2)
    graph.edges.append(edge)
    if edge not in graph.conns:
      graph.conns[edge] = [conn]
    else:
      graph.conns[edge].append(conn)

  def disconnect(graph, node1, node2):
    if (node1, node2) in graph.edges:
      graph.edges.remove((node1, node2))
    if (node2, node1) in graph.edges:
      graph.edges.remove((node2, node1))
    if (node1, node2) in graph.conns:
      del graph.conns[(node1, node2)]
    if (node2, node1) in graph.conns:
      del graph.conns[(node2, node1)]

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
