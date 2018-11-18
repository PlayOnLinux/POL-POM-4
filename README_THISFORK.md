POL-POM-4
=========

PlayOnLinux 4 repository

I've fixed a few glitches I wanted to correct for myself. 
I've decided to create a fork of the main project to share my changes in good open source tradition.

I am keeping track of the changes in the main repository so any release updates are going to be merged into this one.

The changes so far:

1. The colours used in the interface are now read from the system. This means that dark themes display the various elements in the widgets in the colour of those themes. This makes sure that all elements are readable under all conditions.

2. The game list became somewhat long. I noticed that this list is a TreeView control with just one level and a hidden root. I made this TreeView control two-level and added a root with the text "Your games" in a nice big font size. 


How to enable two levels in the TreeView control
The two level system is an open one. It's not based on wine-prefixes but on naming. This way you decide how you want to have your list defined. To define your list do the following:

1. Make sure that there is one game in your list which will be the root item. For instance "Steam".
2. Name all games you want to place under this root item as [Root-Item-Name] - [Name-Of-Your-Game]. For instance "Steam - Crysis"

The list will automatically rearange.


TODO:

1. Some more refining where I run into them.

2. A shelving system is in the making. This is a further development of the TreeView system mentioned above. It allowes the user to define labels (or shelves) in the Options widget and select one of them in a game's Configuration widget. This way the user is free to have entries with hyphens in the gamelist. This is for 80% done.

TFK