# python3
"""Route maker and optimizer for Metroid/Zelda/Castlevania style games."""

from absl import app
# import astar
import elkai
import networkx
import numpy as np

import where


def LoadMap():
  return networkx.drawing.nx_pydot.read_dot('AgentA.dot')


def LoadDependencies():
  dependencies = networkx.drawing.nx_pydot.read_dot('sequence.dot')
  themap = LoadMap()

  items = set(dependencies.nodes)
  locations = set(themap.nodes)
  items -= locations

  unplaced_items = items - set(where.placements.keys())
  if unplaced_items:
    raise ValueError('The following items have no location:\n' +
                     '\n'.join(f'  {it}' for it in sorted(unplaced_items)))
  unknown_locations = set(where.placements.values()) - locations
  if unknown_locations:
    raise ValueError("The following locations aren't on the map:\n" +
                     '\n'.join(f'  {l}' for l in sorted(unknown_locations)))

  print(locations, items)
  costs = np.zeros((len(items), len(items)))
  # find transitive closure
  # set all those edges to -1 in costs
  print(themap)
  # for i in range(costs.rows):
  #   for j in range(costs.columns):
  #     if costs[i, j] != -1:
  #       costs[i, j] = len(
  #           astar.ShortestPath(the_map, where.placements[i],
  #                              where.placements[j]))
  return costs


def main(unused_argv):
  costs = LoadDependencies()
  # print(elkai.solve_int_matrix(costs))


if __name__ == '__main__':
  app.run(main)
