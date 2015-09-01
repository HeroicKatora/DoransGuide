# Doran's Guide

**Website: <http://heroickatora.github.io/DoransGuide/>**

## Description

Doran's guide is a complete guide to item usage as well as a comparison for it 
between different data sets (more on this later). It parses thousands of games
and extracts the item related data from them to create very detailed and 
extensive statistics about their power.

These statistics are then visualized on a web page on which the viewer can also
choose to compare statistics based on one key value. Game data is sorted by
* Version
* Region
* Map
* Queue type
* Participant's rating
* Champion
* Item

But most importantly, instead of just giving the win rate or rate of item usage,
Doran's guide actually shows how these two key values depend on the time and
gold difference at the moment of purchase. This enables players to make more
sophisticated choices about when to buy which item. 

## Documentation

Usage of this project:
1. Run gamedownloader.py (to terminate the download process, press Enter)
2. Run gameanalyer.py (wait or interrupt the script when it's analyzing)

When using the scripts, you will most likely want to set the working directory
as src, since the scripts generate their data into the relative path ../data.
Also, every script that uses the Riot Api needs to be started with the argument
> -k {api-key}

to work properly. Otherwise, it will exit on start-up.

### gameanalyser.py

This python script uses the data generated by gamedownloader.py to generate the
analytical data that contain all data about item usage. Individual item events
are analyzed through the data that they hold.
 1. Version of the game
 2. Region in which the game was played
 3. Map on which the game was player
 4. Queue type in which the event took place
 5. Participant's rating
 6. Champion that the player played
 7. Item that was acquired by the player
 8. Time stamp of the item event, in 10 minute intervals
 9. Gold difference of the player's team relative to the enemy team, in 3k gold intervals

Command line arguments:

option | arguments | effect
-------|-----------|-------
-k | apiKey | [required] Tells the application what api-key to use.

The generated analysis is grouped into files and written to disk in blocks,
in order to save memory. Each file follows the following rules:
* It is located in data/analysis/{region}/{patch}/{mapId}
* Its name is {queue type}.{ranking}.json
* Inside is a map in json format. Keys are string of the format
  
  {region}/{patch}/{mapId}/{queue type}/{ranking}/{championId}/{itemId}/{role}/{lane}
  
  For each of these parts, the values given by the Riot Games api as well as 
  the special key 
  > ANY
  
  are valid.
* The values of the map are json object with the four properties
  * timeAndGoldTable
  * timeTable
  * goldTable
  * winStatistic
  
  The first three contain a list, the last one a single instance of a WinStatistic,
  a list with exactly two entries. The first entry of a WinStatistic is the number
  of games played, the second one the number of games won. 
  timeAndGoldTable is the flat representation of a two dimensional map 
  > map[timeInterval][goldDifference].

### gamedownloader.py

This module loads the game data available from riot. It expects a folder structure
as in the .zip archive provided for the AP Item Category inside the folder itemsets.
It then loads one game after the other in round robin style extracting all item events
from the time line by analyzing each players inventory over the course of each game.
The events are then pickled into the directory data/raw the await further processing.

Command line arguments:

option | arguments | effect
-------|-----------|-------
-k | apiKey | [required] Tells the application what api-key to use. The downloader will automatically change its speed when receiving 429 codes.
-f | --- | Retry previously failed game. By default, the downloader will skip game ids that failed in previous runs

### Other modules

Name | Use|External packages
-----|----|-------
analysis| Contains all data types necessary for the gameanalyser to work correctly|
lolstatic| Gathers some data dynamically from the api but also has Enums to represent basic data types|
matchinfo| Extracts data from a match|
math| Some (unused) wrappers for bisection and ordered arrays|
riotapi| Contains wrapper code for the connection to the endpoint. For example, it limits the amount of accesses to a data point already overloaded or keeps connections alive for reuse| urllib3, certifi  

## Planned
Switching to a database and a web server would give the freedom to index the
game data by a few more key parameters, e.g. the role and lane of the player.  
