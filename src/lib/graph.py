class Graph:
  def __init__(graph):
    graph.nodes = []
    graph.edges = []

  def order(graph):
    return len(graph.nodes)

  def size(graph):
    return len(graph.edges)

  def degree(graph, node):
    return len(graph.neighbors(node))

  def add(graph, node):
    if node not in graph.nodes:
      graph.nodes.append(node)

  def remove(graph, node):
    graph.disconnect(node)
    graph.nodes.remove(node)

  def neighbors(graph, node):
    neighbors = set()
    for n1, n2 in graph.edges:
      if n1 is node:
        neighbors.add(n2)
      elif n2 is node:
        neighbors.add(n1)
    return tuple(neighbors)

  def connect(graph, node1, node2):
    edge = (node1, node2)
    graph.edges.append(edge)

  def disconnect(graph, node1, node2=None):
    if node2 is None:
      for neighbor in graph.neighbors(node1):
        graph.disconnect(node1, neighbor)
      return
    if (node1, node2) in graph.edges:
      graph.edges.remove((node1, node2))
    if (node2, node1) in graph.edges:
      graph.edges.remove((node2, node1))
