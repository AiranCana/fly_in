*This project has been created as part of the 42 curriculum by <your_login_here>.*

# Fly-in — Drone routing simulator

## Description
This project implements a simulation to route a fleet of drones from a start hub to
an end hub through a network of connected zones. It enforces zone and connection
capacity constraints, supports different zone movement costs (normal, restricted,
priority, blocked) and provides both terminal-colour and optional graphical
visualization of the simulation.

The goal is to deliver all drones to the end hub in the minimum number of
discrete simulation turns while respecting occupancy and link capacity rules.

## Instructions
Follow these steps to set up and run the project locally.

- Install dependencies (recommended inside a virtual environment):

```bash
python -m pip install -r requirement.txt
```

- Run the main program (sample):

```bash
python fly_in.py maps/easy/01_linear_path.txt
```

- Common Makefile targets (provided in the repository):
  - `make install` — install project dependencies
  - `make run` — run the main script
  - `make debug` — run the main script under the debugger
  - `make clean` — remove caches and temporary files
  - `make lint` — run `flake8 .` and `mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs`

## Algorithm and Implementation Notes
- Pathfinding: the simulator uses a custom pathfinding routine that accounts for
  zone movement costs and prioritization of `priority` zones. Graph helper
  libraries are not used (for compliance with the assignment rules).
- Turn scheduling: the engine schedules moves per-turn and enforces that drones
  moving into `restricted` zones (2-turn cost) occupy the connection during transit
  and must arrive after the required number of turns.
- Capacity handling: zone `max_drones` and connection `max_link_capacity` metadata
  are respected. Start and end hubs are treated as unlimited capacity.
- Data model: `Hub`, `Connection` and `NetworkFly` models live under
  `generatorData/` and are used by the simulation engine in
  `generatorData/operations/`.

## Visual Representation
- Terminal output: coloured drone and hub names to display live state (uses
  `generatorData/enums.py` color constants). Output format follows the
  specification: each turn prints movements as `D<ID>-<destination>` separated by
  spaces.
- Optional GUI: a simple pygame-based visualiser (`visual.py`) can display the
  network and drone positions. Use it when a graphical representation is needed.

## Example input and expected output
- Input: an example map is in `maps/easy/01_linear_path.txt`.
- Example run output (per-turn lines):

```
D1-roof1 D2-corridorA
D1-roof2 D2-tunnelB
D1-goal D2-goal
```

## How AI was used
AI assistance was used to help add and normalize PEP 257 docstrings across the
codebase and to suggest small refactors. All generated changes were reviewed
and tested locally to ensure they do not change the program behaviour.

## Resources
- Project files and sample maps are included in the repository under `maps/`.
- Recommended tools: `flake8`, `mypy`, `pydocstyle` for style and typing checks.

## Development & Tests
- Run static checks:

```bash
flake8 .
mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
pydocstyle .
```

- Run a quick full-coverage python compile check:

```bash
python -m compileall .
```

## Notes for submission
- Place all files at the repository root (as required by the assignment).
- Include a brief description of algorithmic choices and visual features in this
  README before submission.

---
If you want, I can now run the linters (`flake8`, `mypy`, `pydocstyle`) and report
results, or create a Git commit with these changes. Which do you prefer?