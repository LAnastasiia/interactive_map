# interactive_map
Builds an interactive map (using Python's folium library) according to specific film information given in file (processed with pandas module).

This program builds an interactive multilayer map, which points filming
locations with markers. User enters the year to explore film locations of
specific year (else it will be assigned to the default value). Map contains 3 layers:

*  simple map, presented in watercolor, openstreets, landscape and bright interpretations, user
also can put his own markers (blue) on this layer.

*  map layer with marked (light blue pointers) places of filming and place
of user's home (due to address, given by user).

*  map layer with painted in different colors (according to population
data) countries; information about population is taken from world.json file.
