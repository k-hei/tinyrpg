from math import inf
from copy import deepcopy

class Graph:
  def __init__(graph, nodes=None, edges=None):
    graph.nodes = nodes or []
    graph.edges = edges or []

  def copy(graph):
    return Graph(nodes=graph.nodes.copy(), edges=graph.edges.copy())

  def order(graph):
    return len(graph.nodes)

  def size(graph):
    return len(graph.edges)

  def ends(graph):
    return [n for n in graph.nodes if graph.degree(n) == 1]

  def degree(graph, node):
    return len(graph.neighbors(node))

  def add(graph, node):
    if node not in graph.nodes:
      graph.nodes.append(node)

  def remove(graph, node):
    graph.disconnect(node)
    if node in graph.nodes:
      graph.nodes.remove(node)
    graph.edges = [(n1, n2) for n1, n2 in graph.edges if n1 is not node and n2 is not node]

  def neighbors(graph, node):
    neighbors = set()
    for n1, n2 in graph.edges:
      if n1 is node:
        neighbors.add(n2)
      elif n2 is node:
        neighbors.add(n1)
    return tuple(neighbors)

  def tail(graph, head):
    for n1, n2 in graph.edges:
      if n1 is head:
        return n2
      if n2 is head:
        return n1

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

  def distance(graph, start, goal):
    if start is goal:
      return 0
    distance = inf
    for neighbor in graph.neighbors(start):
      subgraph = graph.copy()
      subgraph.remove(start)
      d = 1 + subgraph.distance(neighbor, goal)
      if d < distance:
        distance = d
    return distance

  def path(graph, start, goal):
    if start is goal:
      return [start]
    path = []
    for neighbor in graph.neighbors(start):
      subgraph = graph.copy()
      subgraph.remove(start)
      subpath = subgraph.path(neighbor, goal)
      if not subpath:
        continue
      subpath = [start] + subpath
      if not path or len(subpath) < len(path):
        path = subpath
    return path
