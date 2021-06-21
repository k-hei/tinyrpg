from lib.graph import Graph

class TownGraph(Graph):
  def link_area(graph, link):
    for area in graph.nodes:
      if next((l for l in area.links.values() if link is l), None):
        return area
