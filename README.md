*This project has been created as part of the 42 curriculum by <your_login>.*
 
# Fly-in
 
## Description
 
Fly-in is a drone routing simulator. Given a map file describing a network
of zones (`hubs`) connected by links, the program routes a fleet of drones
from a single `start` zone to a single `end` zone in as few simulation
turns as possible, while respecting per-zone capacity, per-connection
capacity, and per-zone movement costs (`normal`, `priority`, `restricted`,
`blocked`).
 
The project is split into four layers:
 
- **Parsing** (`generatorData/parser.py`): reads the custom map file
  format and turns it into plain dictionaries, with line-level error
  reporting.
- **Data model** (`generatorData/genDataZones.py`, `generatorData/enums.py`):
  immutable, `pydantic`-validated `Hub`, `Connection` and `NetworkFly`
  models, built entirely from the parsed data, without any graph-logic
  library.
- **Pathfinding** (`generatorData/generateRutes.py`): a hand-written
  Dijkstra plus a Yen-style search for several disjoint low-cost routes,
  used to spread drones across independent paths instead of a single
  corridor.
- **Simulation** (`generatorData/operations/`): `Simulation` tracks live
  zone/connection occupancy, `Drones` tracks each drone's own state and
  route progress, and `Operate` drives the turn-by-turn scheduling,
  capacity checks, and colored terminal output.
A `pygame`-based graphical view (`visual.py`, launched via
`visualicer.py`) complements the colored terminal output with a
node-and-edge rendering of the network and animated drone movement.
 
## Instructions
 
### Install
 
```bash
make install
```
 
Creates a local virtual environment (`.venv`) and installs everything
listed in `requirement.txt` (`pydantic`, `strenum`, `mypy`, `flake8`,
`pygame`).
 
### Run a simulation (terminal output)
 
```bash
make run maps/easy/01_linear_path.txt
```
 
Prints one line per turn (`Turn N: D1-hub, D2-corridorA, ...`) until every
drone has reached the end zone.
 
### Run the graphical view
 
```bash
make visual maps/easy/01_linear_path.txt
```
 
> Requires `visual.py` at the project root (see note below).
 
### Run the benchmark suite
 
```bash
make run_all
```
 
Runs every map listed in `prube.py` and reports `PASS`/`NO PASS` against
the turn-count targets from the subject (VII.7), without printing the
turn-by-turn log.
 
> Requires the `maps/` directory with the subject's sample maps at the
> project root (see note below).
 
### Other targets
 
```bash
make debug maps/easy/01_linear_path.txt   # runs under pdb
make lint                                  # flake8 + mypy (standard flags)
make lint-strict                           # flake8 + mypy --strict
make clean                                 # removes __pycache__ / .mypy_cache
```
 
### A note on two files this archive is missing
 
`visualicer.py` imports `from visual import visual`, and `prube.py`
references maps under `maps/`, but neither `visual.py` nor `maps/` are
present in this copy of the repository. Both `make visual` and
`make run_all` will fail until they're added back (most likely they were
left out of the archive by mistake, e.g. an overly broad `.gitignore` or
`tar --exclude` rule).
 
## Resources
 
### References
 
- Dijkstra's algorithm and Yen's k-shortest-paths algorithm (used as the
  basis for the custom, dependency-free pathfinding in
  `generateRutes.py` — no graph library was used, per the subject's
  constraints).
- [Pydantic documentation](https://docs.pydantic.dev/) — model
  validation, `model_validator`, frozen models.
- [pygame documentation](https://www.pygame.org/docs/) — window/surface
  management, event loop, drawing primitives.
- Python standard library docs for `heapq` (priority queue used by
  Dijkstra) and `dataclasses`.
### AI usage
 
AI assistance was used throughout development, primarily for:
 
- **Debugging.** Diagnosing and fixing concrete runtime bugs (e.g.
  incorrect off-by-one capacity checks, mutable Pydantic dict defaults,
  forward-reference `NameError`s, duplicate module imports causing
  `isinstance` mismatches, `flip()`/`fill()` ordering bugs in the
  `pygame` renderer) by reproducing them in isolation and verifying the
  fix before applying it.
- **Code review.** Reviewing new classes and methods for type-safety
  issues (`mypy`), logic bugs, and consistency with the subject's rules
  (e.g. capacity semantics, the 2-turn cost of `restricted` zones,
  bidirectional connection lookups).
Every AI-assisted change was tested against real map data and manually
reviewed before being kept, and all contributors can explain and defend
any part of the codebase during peer evaluation.
 
## Algorithm choices and implementation strategy
 
### Parsing
 
The map file is read line by line into a small `Lecture` helper that
keeps the original line number and raw text alongside the parsed
`type`/`data` split, so that any downstream error (`Parser_error`) can
report exactly where in the file it went wrong, not just what went
wrong.
 
### Data model
 
`Hub`, `Connection` and `NetworkFly` are frozen `pydantic` models: once
parsed, the network definition never changes for the rest of the run.
All mutable, per-simulation state (how many drones currently sit in a
zone, how many are traversing a connection) lives separately, in
`Simulation`, so the same parsed `NetworkFly` could in principle drive
several independent simulations without re-parsing.
 
`NetworkFly.hub_by_name` gives O(1) hub lookup by name (built once, in
the model's `after` validator), and `found_connects` is overloaded to
either return every connection touching a given `Hub` (for graph
traversal) or the single `Connection` between an exact pair of hub names
(via a `frozenset` key, so `a-b` and `b-a` resolve to the same
connection regardless of which order the map file wrote them in).
 
### Pathfinding (`generateRutes.Generator`)
 
- **Single path**: a hand-written Dijkstra (`__dijkstra` /
  `explore_neighbor`) using `heapq` as the priority queue, giving
  O((V+E) log V) instead of a linear scan for the minimum-distance node.
  Movement cost is 2 for `restricted` zones and 1 otherwise; `blocked`
  zones are excluded from traversal entirely; zones of type `priority`
  are preferred via a tiny tie-break penalty that never changes the
  reported integer turn cost.
- **Several disjoint paths**: on top of the first path, the generator
  repeatedly forbids one edge of an already-found path and reruns
  Dijkstra, keeping the cheapest genuinely new path found (a simplified
  Yen's algorithm). It keeps adding paths only while both are true:
  - the combined bottleneck capacity of the paths found so far is still
    below `nb_drones` (more paths beyond that point wouldn't help), and
  - the new candidate doesn't cost more than `FACTOR_COST` (currently
    `1.01`) times the cheapest path found (a longer detour isn't worth
    it just to add parallelism).
  This means the number of alternative routes is decided by the map
  itself, not by a fixed parameter — a map with one wide corridor gets
  one route; a map with several genuinely useful parallel routes gets
  several.
### Route assignment (`Operate.__prepare_asign_route` / `__asign_route`)
 
Each route's *bottleneck capacity* (the minimum `max_drones`/
`max_link_capacity` along it) is used as a weight. Drones are split
across routes proportionally to that weight using the largest-remainder
method (exact proportional shares are computed, truncated to integers,
and the leftover drones go to the routes with the largest fractional
remainder first) — so a route that can only carry one drone at a time
isn't assigned the same number of drones as one that can carry several.
Drones are then interleaved across routes (not assigned in contiguous
blocks) so that drones queued close together in time use different
connections in parallel instead of competing for the same one.
 
### Turn scheduling (`Operate`)
 
Each turn, `order_target` selects every drone not yet at `end_hub`,
sorted by how many steps remain in its own route (closest to arrival
first) and then by id as a tiebreaker — this lets drones near the front
of a corridor clear a hub before the drones behind them try to enter it,
avoiding turns wasted on avoidable congestion.
 
For each selected drone, `__prepare_move` reserves connection and zone
capacity for a first attempt, or simply continues an already-reserved
move if the drone is mid-transit. `__can_move_now` enforces the extra
turn required by `restricted` zones. `__movement` then actually advances
drones whose move is both prepared and due, prints the colored
`Turn N: ...` line, and returns a snapshot of drone states for that turn
(used by the `pygame` view to animate/step through the run afterwards).
 
## Visual representation
 
### Terminal (always available, no extra dependencies)
 
Every drone movement is printed with the destination zone's configured
ANSI color (`Hub.color`); zones without an explicit color are printed
cycling through a fixed rainbow of colors, offset randomly per call so
consecutive prints don't all start on the same hue. Drones currently in
transit through a `restricted` zone's connection are printed as
`D<id>-'<hub1>-<hub2>'` instead of a hub name, colored per the two
endpoint hubs, so it's clear from the log alone which drones are mid
flight rather than sitting still.
 
### Graphical (`pygame`)
 
The graphical view reuses the same `Hub.x`/`Hub.y` coordinates from the
map file to lay out the network (no separate graph-layout algorithm is
needed), draws every connection as a line and every hub as a colored
node (color by zone type, with a distinct outline for `start`/`end`),
and animates each drone moving between hubs frame by frame rather than
jumping between positions, using the turn-by-turn snapshots recorded
during the run. Arrow keys / A-D step forward and backward through the
recorded history so a run can be reviewed turn by turn after the fact,
not just watched live.
 
Together, the two representations serve different purposes: the
terminal log is the exact, copyable record of what happened each turn
(and works over SSH / in CI with no display), while the graphical view
gives an at-a-glance sense of where congestion is building up across the
whole network — useful for judging whether a route assignment or
scheduling decision was actually a good one.