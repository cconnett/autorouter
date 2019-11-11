# python3
"""Route maker and optimizer for Metroid/Zelda/Castlevania style games."""

import sys

from absl import app
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


def Validate(items, where, locations):
  unplaced_items = items - set(where.keys())
  if unplaced_items:
    raise ValueError(
        f'The following {len(unplaced_items)} items have no location:\n' +
        '\n'.join(f'  {it}' for it in sorted(unplaced_items)))
  unknown_locations = set(where.values()) - locations
  if unknown_locations:
    raise ValueError("The following locations aren't on the map:\n" + '\n'.join(
        f'  {l}' for l in sorted(unknown_locations)))
  assert not locations & where.keys(), locations & where.keys()


def main(unused_argv):
  dependencies = networkx.drawing.nx_pydot.read_dot(
      'data/AgentA/dependencies.dot')
  themap = LoadMap()
  where = LoadItemLocations()

  items = set(dependencies.nodes) | set(where.keys())
  locations = set(themap.nodes)
  blocking_locations = set(dependencies.nodes) & locations
  items -= locations

  Validate(items, where, locations)

  items = sorted(items)
  start = items.index('start')
  end = items.index('end')
  items[0], items[start] = items[start], items[0]
  items[-1], items[end] = items[end], items[-1]

  apsp = dict(
      networkx.algorithms.shortest_paths.weighted.
      all_pairs_bellman_ford_path_length(
          themap, weight=lambda _1, _2, attrs: int(attrs.get('weight', 1))))
  apsp_path = dict(
      networkx.algorithms.shortest_paths.weighted.all_pairs_bellman_ford_path(
          themap, weight=lambda _1, _2, attrs: int(attrs.get('weight', 1))))
  costs = np.zeros((len(items), len(items)), int)
  for i in range(len(items)):
    for j in range(len(items)):
      if i == j:
        costs[i, j] = 0
      elif items[i] == 'end' or items[j] == 'start':
        costs[i, j] = -1
      else:
        costs[i, j] = apsp[where[items[i]]][where[items[j]]]
  del i, j
  for item_i in items:
    blockable_locations_start_to_i = (
        set(apsp_path[where['start']][where[item_i]]) & blocking_locations)
    for block in blockable_locations_start_to_i:
      themap2 = themap.copy()
      themap2.remove_node(block)
      try:
        # Check if a path still exists.
        if where[item_i] == block:
          raise networkx.NetworkXNoPath
        networkx.algorithms.shortest_paths.generic.shortest_path(
            themap2, where['start'], where[item_i])
      except networkx.NetworkXNoPath:
        for requirement in dependencies[block]:
          # print(f'start->{item_i} needs {requirement} because it blocks {block}')
          dependencies.add_edge(item_i, requirement)

  item_precedence = dict(networkx.all_pairs_shortest_path_length(dependencies))
  for item_i in item_precedence:
    if item_i not in items:
      continue
    for item_j in item_precedence[item_i]:
      # print(f'Cannot go from {item_i} to {item_j}.')
      costs[items.index(item_i), items.index(item_j)] = -1

  if len(sys.argv) == 1:
    print('NAME: AgentA')
    print('TYPE: SOP')
    print('EDGE_WEIGHT_TYPE: EXPLICIT')
    print('EDGE_WEIGHT_FORMAT: FULL_MATRIX')
    print(f'DIMENSION: {len(items)}')
    print('EDGE_WEIGHT_SECTION')
    print(len(items))
    for i in range(len(items)):
      for j in range(len(items)):
        print(f'{costs[i,j]:<4d} ', end='')
      print()
  else:
    tourdata = open(sys.argv[1]).readlines()
    tour = [int(node) - 1 for node in tourdata[6:6 + len(items)]]
    for index, prev in zip(tour[1:], tour):
      print(
        f'Go {costs[prev, index]} steps to {where[items[index]]} and get {items[index]}.'
      )

if __name__ == '__main__':
  app.run(main)
