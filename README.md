This project is meant to provide a model for a signal light that controls an intersection.
The specification will grow as time goes by.  At its root, it will:
100: Control an intersection of N roads
100-1: Initially, N is fixed at 4, with names North, South, East, West
100-2: Initially, only 1 road can be "active" at a time (have a green light)
200: Have a light-set for each road
200-1: Initially, the lights will only be green, yellow, and red.
200-2: The duration of the lights will be green: 27 seconds, yellow 3 seconds, red - as long as the road is not active
300: Shall provide methods to determine the intersection / signal's status
300-1: Getter on the current active road, by name 
300-2: Getter on the current light for a given direction (input by name)
400: Main driver for test
400-1: Shall create one instance of the signal class
400-2: Shall, every second, call the first getter to get the active direction and the second getter to get the current color on said direction, printing a message with both
500: Shall provide a REST API
500-1: Shall provide a PUT method on / to create a new signal instance. Returns an ID for the signal
500-2: Shall provide a GET method on / to provide an array of existing signal IDs
500-3: Shall provide a GET method on /<signal-id>/direction to get the current active direction of the provided signal
500-4: Shall provide a GET method on /<signal-id>/<direction>/color to get the current active color of the indicated direction
500-5: Shall provide a GET method on /<signal-id> to get the current active direction and color of the signal
