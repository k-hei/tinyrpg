from lib.graph import Graph

class TownGraph(Graph):
  def link_area(graph, link):
    for area in graph.nodes:
      if link in area.links.values():
        return area
