# Doran's Guide

## Description

Doran's guide is a complete guide to item usage as well as a comparison for it 
between different data sets (more on this later). It parses thousands of games
and extracts the item related data from them to create very detailed and 
extensive statistics about their power.

These statistics are then visualized on a web page on which the viewer can also
choose to compare statistics based on one key value. Game data is sorted by
* version
* region
* map
* queue type
* elo of the player
* champion
* item
But most importantly, instead of just giving the win rate or rate of item usage,
Doran's guide actually shows how these two key values depend on the time and
gold difference at the moment of purchase. This enables players to make more
sophisticated choices about when to buy which item. 

## Planned
Switching to a database and a web server would give the freedom to index the
game data by a few more key parameters, e.g. the role and lane of the player.  
