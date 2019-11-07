# python3
"""Route maker and optimizer for Metroid/Zelda/Castlevania style games."""

from absl import app
# import astar
import elkai
import networkx
import numpy as np


def LoadItemLocations():
  ret = {}
  for line in open('data/AgentA/itemlocations.txt'):
    item, location = line.split(':')
    ret[item.strip()] = location.strip()
  return ret


def LoadMap():
  themap = networkx.drawing.nx_pydot.read_dot('data/AgentA/map.dot')
  for edge in themap.edges:
    if themap.edges[edge].get('dir') != 'forward':
      u, v, _ = edge
      themap.add_edge(v, u)
  return themap



def main(unused_argv):
  dependencies = networkx.drawing.nx_pydot.read_dot(
      'data/AgentA/dependencies.dot')
  themap = LoadMap()
  where = LoadItemLocations()

  items = set(dependencies.nodes)
  locations = set(themap.nodes)
  items -= locations

  unplaced_items = items - set(where.keys())
  if unplaced_items:
    raise ValueError(
        f'The following {len(unplaced_items)} items have no location:\n' +
        '\n'.join(f'  {it}' for it in sorted(unplaced_items)))
  unknown_locations = set(where.values()) - locations
  if unknown_locations:
    raise ValueError("The following locations aren't on the map:\n" + '\n'.join(
        f'  {l}' for l in sorted(unknown_locations)))

  apsp = dict(networkx.all_pairs_shortest_path_length(themap))
  nodes = list(themap.nodes)
  costs = np.zeros((len(nodes), len(nodes)), int)
  for u, path_dict in apsp.items():
    for v, cost in path_dict.items():
      costs[nodes.index(u), nodes.index(v)] = cost if cost > 0 else -1

  tour = elkai.solve_int_matrix(costs)
  for index in tour:
    print(nodes[index])


if __name__ == '__main__':
  app.run(main)
