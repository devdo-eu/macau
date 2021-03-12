# Macau
![License](https://img.shields.io/github/license/devdo-eu/macau?style=plastic)
![Tests](https://github.com/devdo-eu/macau/workflows/Tests/badge.svg?branch=master)
![Quality](https://github.com/devdo-eu/macau/workflows/Quality/badge.svg?branch=master)
![lgtm-grade](https://img.shields.io/lgtm/grade/python/github/devdo-eu/macau?style=plastic)
![lgtm-alerts](https://img.shields.io/lgtm/alerts/github/devdo-eu/macau?style=plastic)
![coverage](https://img.shields.io/codecov/c/github/devdo-eu/macau?style=plastic)
![last-commit](https://img.shields.io/github/last-commit/devdo-eu/macau?style=plastic)
![code-size](https://img.shields.io/github/languages/code-size/devdo-eu/macau?style=plastic)

This is the Macau project.   
Install the [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
After installation please setup environment with:  
`conda env create -f environment.yml`  
Next change environment with:  
`conda activate macau`  
now you can run the game locally using `python macau.py`.

There are unit tests for this project.  
You can run tests using `pytest` in project directory.

# Features  

![movie](./media/JeIjc1OvHi.gif)  

This is standard [Macau](https://en.wikipedia.org/wiki/Macau_(card_game)) game.
After start of `macau.py` script you will see:  
```
Welcome to Macau Game!
How many players will play?:
```
You can choose any number of players bigger than 2.  
After you enter number of players you need to enter starting number of cards:  
```
Welcome to Macau Game!
How many players will play?: 2
How many cards on start?:
```
You can choose any number of players bigger than 3.  
Number of decks will be calculated.  
Next step is to enter names of all players:  
```
Welcome to Macau Game!
How many players will play?: 2
How many cards on start?: 3
Game will be played with 1 decks.
Enter name for player#1 :
```
If name of player contains `CPU` then this player will be controlled by a computer.  
This means that player with name `Test_CPU` will be cpu-player.  
Game window looks like:
```
Grzesiek Turn Now!

Grzesiek
---------------------Punishments---------------------
Cards: 0
Skip turns: 0
----------------------Requests-----------------------
Color: hearts
Value: None
----------------------Players------------------------
Grzesiek has: 2 cards on hand.
Aga has: 2 cards on hand.
-----------------------Table-------------------------
Cards in deck: 31
Cards on table: 16
On top: tiles A
------------------------Hand-------------------------
tiles 5, *hearts 4*
-----------------------------------------------------
*color value* -> means that this card can be played
Which card(s) from your hand do you want to play?:
```

Cards which you can play are marked with stars `*`.  
You can play card from your hand with `color value` line.  
For example: `hearts 3`  

If you have pack of cards on your hand e.g. like: `hears 7, tiles 7, pikes 7`  
then you can put on table all of them in one move.  
Pack is 3 or 4 cards with same value, jacks, aces, queens, 2, 3 and 4 included. 

### CPU self play
If all players in game will have `CPU` inside their name,   
then only cpu players will play macau.  
In such a case, the game window will look like:  
```
CPU_A plays: hearts A, clovers A, tiles A | on hand: 2 cards.
CPU_A plays: clovers | on hand: 2 cards.
CPU_B plays: clovers 6 | on hand: 4 cards.
CPU_A plays: clovers K | on hand: 1 cards.
CPU_B has no move.
CPU_B will have to take a card.
1 cards dealt to CPU_B. | on hand: 5 cards.
CPU_A plays: pikes K | on hand: 0 cards.
CPU_B will have to take 5 cards.
5 cards dealt to CPU_B. | on hand: 10 cards.
CPU_B plays: pikes 2 | on hand: 9 cards.
Game won by: ['CPU_A'] !
```

# Rules 

If you play jacks, then you can request cards with chosen value.  
If you play aces, then you can request cards with chosen color.

Cards with values of 2 and 3 are used to attack other players,  
if a player fails to defend against these cards he/she will have to draw  
additional cards from the deck.

Cards with value of 4 are used also to attack other players,  
if a player fails to defend against it - then will have to skip some turns.

King of pikes will punish with cards player behind current player  
with no chance for defend.  
King of hearts will add 5 cards to penalty for next player.  

If no special card is on table, then rule `All on Queen, Queen on all` applies.

When one player will have only one card left on hand,  
then `Name has Macau!` message will be shown on top of player screen.  

Game will end if one or more players finish round with no cards on hand.

# Development
This project is starting point for more complex development.
+ implemented:
  + macau card game logic for 1 deck and max 6 players
  + terminal interface
  + cpu players
  + macau can be played with more than 1 deck and more than 6 players
  + cpu players can play with packs of card

# License

MIT License

Copyright (c) 2021 Grzegorz Maciaszek
