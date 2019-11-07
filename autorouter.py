# python3
"""Route maker and optimizer for Metroid/Zelda/Castlevania style games."""

from absl import app
# import astar
import elkai
import networkx
import numpy as np

INFINITY = 2**26


def LoadItemLocations():
  ret = {}
  for line in open('data/AgentA/itemlocations.txt'):
    item, location = line.split(':')
    ret[item.strip()] = location.strip()
  return ret


def LoadMap():
  themap = networkx.drawing.nx_pydot.read_dot('data/AgentA/map.dot')
  themap = networkx.DiGraph(themap)
  for edge in themap.edges:
    if themap.edges[edge].get('dir') != 'forward':
      u, v = edge
      themap.add_edge(v, u, **themap.edges[edge])
  return themap


def main(unused_argv):
  dependencies = networkx.drawing.nx_pydot.read_dot(
      'data/AgentA/dependencies.dot')
  themap = LoadMap()
  where = LoadItemLocations()

  items = set(dependencies.nodes) | set(where.keys())
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

  items = list(items)
  start = items.index('start')
  end = items.index('end')
  items[0], items[start] = items[start], items[0]
  items[-1], items[end] = items[end], items[-1]

  apsp = dict(
      networkx.algorithms.shortest_paths.weighted
      .all_pairs_bellman_ford_path_length(
          themap, weight=lambda _1, _2, attrs: int(attrs.get('weight', 1))))
  item_precedence = dict(networkx.all_pairs_shortest_path_length(dependencies))
  costs = np.zeros((len(items), len(items)), int)
  for i in range(len(items)):
    for j in range(len(items)):
      if i == j:
        costs[i, j] = INFINITY
        continue
      try:
        cost = apsp[where[items[i]]][where[items[j]]]
        costs[i, j] = (cost if cost > 0 else INFINITY)
        if items[i] == 'end':
          costs[i, j] = INFINITY
        if items[i] == 'start':
          continue
        if (items[i] in item_precedence and
            items[j] not in item_precedence[items[i]]):
          costs[i, j] = INFINITY
      except:
        print(items[i], items[j])
        print(where[items[i]], where[items[j]])
        import pdb
        pdb.post_mortem()

  tour = elkai.solve_int_matrix(costs)
  for index in tour:
    print(items[index])


if __name__ == '__main__':
  app.run(main)
