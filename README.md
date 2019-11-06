# autorouter

An automatic route finder and optimizer for Metroid®/Zelda®/Vania-type games.

## Overview

### What type of games?

There's a genre of action-role-playing-games that's sometimes referred to as
Metroidvanias. It also includes Legend of Zelda® series games. The key aspect of
these game worlds are that they are initially quite closed; as players explore
and complete objectives, they find items that allow access to new areas of the
game world. The entrances to these new areas are often found in already explored
areas; the entrances are now passable by using the newly acquired items.

Players need to backtrack to access the new areas. This creates a non-linearity
in the optimal route. Finding the optimal route becomes a Sequential Ordering
Problem, a subset of the Travelling Salesperson problem (TSP). The edge costs in
this ordering problem are furthermore derived from pairwise shortest path on the
game world graph.

### Input data

Here's the catch: The autorouter needs a game world to analyze. Describing this
game world in a way that's useful is unfortunately a lot of work. The project
aims to make tools that simplify writing the description of the game world.

### Isn't Travelling Salesperson a really hard problem? NP-Complete?

In the general sense, yes; but in practice, TSP solvers can achieve optimal
results on huge problems. The record for optimal solving of non-trivial
instances is 109,399 cities/nodes. It's safe to say that the a state-of-the-art
TSP solver will give an optimal or near-optimal result.

## Tools

### Autorouter

The main tool in this project is Autorouter itself. This tool needs as input — a
graph of locations in the world map; a graph of item dependencies; and a
location for each item. Since items often unlock regions of the game world and
not specific items, locations can be put in the item dependency graph: All items
that are reachable only by going into a particular region will depend on being
able to access that region.

### Mapmaker

It's a tedious process to describe every area of a game world and which other
areas it connects to. Mapmaker is a tool to annotate an image of the game world
and produce a geographical graph that works as input to Autorouter.
