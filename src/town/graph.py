from lib.graph import Graph

class TownGraph(Graph):
  def link_area(graph, link):
    return next((a for a in graph.nodes for l in a.links.values() if link is l), None)
