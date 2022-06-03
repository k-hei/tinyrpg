from lib.graph import Graph


class WorldGraph(Graph):

  @staticmethod
  def hash_area(area):
    try:
      return area.key
    except AttributeError:
      pass

    try:
      return area.__name__
    except AttributeError:
      pass

    try:
      return type(area).__name__
    except AttributeError:
      pass

  @staticmethod
  def hash_link(area, link_id):
    return WorldGraph.hash_area(area), link_id

  def tail(graph, area, link_id):
    link = graph.hash_link(area, link_id)
    for n1, n2 in graph.edges:
      if graph.hash_link(*n1) == link:
        return n2
      if graph.hash_link(*n2) == link:
        return n1

  def link_area(graph, link):
    return next((a for a in graph.nodes for l in a.links.values() if link is l), None)
