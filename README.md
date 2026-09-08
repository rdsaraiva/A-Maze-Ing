*This project has been created as part of the 42 curriculum by dcarneir, roda-fon.*

# A-Maze-ing — This is the way

## Description

**A-Maze-ing** is a Python maze generator and visualizer. Given a simple text
configuration file, the program generates a maze — either a **perfect maze**
(exactly one path between entrance and exit, no loops) or a **Pac-Man-style
board** (fully connected, open corners and centre, at least two independent
routes, rare dead-ends) — writes it to an output file using a compact
hexadecimal wall encoding, and displays it visually (ASCII in the terminal
and/or a graphical MiniLibX window).

The goal of the project is twofold:
- Explore classic maze-generation algorithms (recursive backtracker, Prim's,
  Kruskal's, etc.), randomness, and the graph-theory link between perfect
  mazes and spanning trees.
- Package the generation logic as a **reusable, pip-installable module**
  (`mazegen`) that can be imported by future projects, independently of the
  CLI/visualization code.

## Instructions

### Requirements
- Python 3.10+
- (Optional, for graphical mode) MiniLibX and its Python bindings

### Installation
```bash
git clone <repo-url>
cd a-maze-ing
make install
```
`make install` creates/uses a virtual environment and installs the
dependencies listed in `requirements.txt` (or via `pyproject.toml`).

### Running the project
```bash
python3 a_maze_ing.py config.txt
```
- `a_maze_ing.py` is the main entry point.
- `config.txt` is the configuration file described below (a default one is
  provided at the root of the repository).

### Makefile targets
| Target        | Description                                                  |
|---------------|---------------------------------------------------------------|
| `make install`| Installs project dependencies                                 |
| `make run`    | Runs the main script with the default config file              |
| `make debug`  | Runs the main script under `pdb`                               |
| `make clean`  | Removes caches (`__pycache__`, `.mypy_cache`, etc.)             |
| `make lint`   | Runs `flake8 .` and `mypy .` with the required flags            |
| `make lint-strict` | (optional) Runs `flake8 .` and `mypy . --strict`           |

### Running the tests (not graded)
```bash
pytest
```

## Configuration file format

The configuration file is a plain text file with one `KEY=VALUE` pair per
line. Lines starting with `#` are treated as comments and ignored.

| Key           | Description                        | Example              | Required |
|---------------|-------------------------------------|-----------------------|----------|
| `WIDTH`       | Maze width, in cells                | `WIDTH=20`            | yes      |
| `HEIGHT`      | Maze height, in cells               | `HEIGHT=15`           | yes      |
| `ENTRY`       | Entry coordinates `x,y`             | `ENTRY=0,0`           | yes      |
| `EXIT`        | Exit coordinates `x,y`              | `EXIT=19,14`          | yes      |
| `OUTPUT_FILE` | Path of the generated output file   | `OUTPUT_FILE=maze.txt`| yes      |
| `PERFECT`     | `True` for a perfect maze (single path, no loops); `False` (default) for a Pac-Man-style board with loops | `PERFECT=True` | yes |
| `SEED`        | Random seed, for reproducible mazes | `SEED=42`             | yes (for reproducibility) |

A ready-to-use default configuration file, `config.txt`, is provided at the
root of the repository.

Any malformed line, missing mandatory key, out-of-bounds coordinate, or
otherwise impossible parameter combination is reported to the user with a
clear error message; the program never crashes on invalid input.

## Maze generation algorithm

**Algorithm chosen: Recursive Backtracker (randomized depth-first search).**

Starting from a grid where every cell has all four walls closed, the
algorithm picks a starting cell, marks it as visited, and repeatedly moves
to a random unvisited neighbour, knocking down the wall between the current
cell and that neighbour as it goes. When a cell has no unvisited neighbour
left, the algorithm backtracks along the path it came from (hence the name)
until it finds a cell that still has an unvisited neighbour, and continues
from there. This carves a spanning tree of the grid: by construction there
is exactly one path between any two cells, which is exactly what the
`PERFECT=True` mode requires.

To produce the `PERFECT=False` (Pac-Man-style) board, the same spanning
tree is used as a base and then adapted:
- A controlled number of extra walls are removed (walls that were left
  standing by the backtracker) to introduce loops, giving at least two
  independent routes between the corners/centre and reducing dead-ends.
- The four corners and the centre of the grid are explicitly forced open,
  as required for ghost/super-pac-gum spawn points and the player's start.
- The generator checks corridor width (never wider than 2 cells) and
  connectivity after this loop-adding pass, and also carves the required
  "42" pattern of fully closed cells.

### Why this algorithm?

The recursive backtracker is simple to implement and reason about, and it
maps directly onto the graph-theory idea given in the subject: a perfect
maze is a spanning tree, and the recursive backtracker is essentially a
randomized DFS spanning-tree construction. This made satisfying
`PERFECT=True` almost immediate. It also produces long, winding corridors
with relatively few short dead-ends compared to some other algorithms
(e.g. plain Prim's), which made it a good starting point to "braid" into
the Pac-Man board by removing a small, controlled number of extra walls
afterward, rather than having to fight a very dense maze of short
dead-ends. We did not implement any bonus features (no support for
multiple algorithms, no animation, no zero-dead-end braided bonus).

## Reusable module (`mazegen`)

All maze-generation logic lives in a single reusable class, `MazeGenerator`,
inside the standalone `mazegen` package, independent from the CLI and
display code. It is distributed as a pip-installable package
(`mazegen-1.0.0-py3-none-any.whl` / `.tar.gz`) built from the sources at
the root of this repository, and is released under the license described in
[`LICENSE.md`](LICENSE.md).

### Building the package
```bash
python3 -m pip install --upgrade build
python3 -m build
```
This produces the `.whl` and `.tar.gz` archives under `dist/`.

### Installing it in another project
```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Basic usage
```python
from mazegen import MazeGenerator

# Instantiate the generator with custom parameters
generator = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit=(19, 14),
    perfect=True,
    seed=42,
)

# Generate the maze
maze = generator.generate()

# Access the generated structure (grid of cells with wall information)
grid = maze.grid

# Access a solution (shortest path from entry to exit)
path = maze.solution  # e.g. ['N', 'E', 'E', 'S', ...]
```

> The internal structure returned by `mazegen` is not necessarily the same
> hexadecimal format used by the output file produced by `a_maze_ing.py`;
> `a_maze_ing.py` is responsible for converting it to that file format.

## Resources

- Wikipedia — "Maze generation algorithm"
- Jamis Buck, *Buckblog* — series of articles on maze generation algorithms
  (recursive backtracker, Prim's, Kruskal's)
- Course material and Wikipedia on spanning trees, to understand why a
  recursive backtracker produces a perfect maze
- Python official documentation for the `typing` and `argparse` modules
- `mypy` and `flake8` documentation for the linting configuration
- MiniLibX documentation (school intranet), for the graphical rendering mode

### AI usage

Every AI suggestion was reviewed, tested, and understood by the team before
being integrated; no unreviewed AI-generated code was merged into the
project. All final design and implementation decisions (in particular the
choice of the recursive backtracker algorithm and the module architecture)
were made and are fully understood by the team.

## Team and project management

### Roles
| Member      | Role                                                                 |
|-------------|-----------------------------------------------------------------------|
| `dcarneir`  | Implemented the "42" pattern generation and the Pac-Man mode (`PERFECT=False`: loop-adding pass, open corners/centre, dead-end reduction) |
| `roda-fon`  | Implemented the rest of the project (config parsing, recursive backtracker core, output file writer, visual rendering, error handling, `mazegen` package) |

Both members worked together on the `README.md`, the `Makefile`, and
building the compressed reusable package (`mazegen-*.tar.gz` / `.whl`).

### Planning
The work was split by module from the start: `dcarneir` took ownership of
the "42" pattern and the Pac-Man mode, `roda-fon` took ownership of the
configuration parsing, the recursive backtracker core, the output writer
and the visual rendering. The two agreed early on the shared internal grid
representation (which cell stores which walls) so that both parts could be
developed in parallel without waiting on each other. The initial plan was
to have the core generator and file output working first, then add the
Pac-Man mode and the "42" pattern on top, and finish with the visual
rendering and polishing (linting, docstrings, README). This order was kept
until the end; the main adjustment was spending more time than expected on
making the Pac-Man mode satisfy every constraint at once (loops, open
corners/centre, corridor width, rare dead-ends), which pushed the visual
polishing to the last days.

### What worked well / what could be improved
- **What worked well:** agreeing on the grid/wall representation before
  writing any code avoided integration problems when merging the two parts;
  splitting the work by mode (perfect vs. Pac-Man) rather than by layer
  (generation vs. display) let each person own a feature end-to-end.
- **What could be improved:** we underestimated how long the Pac-Man mode
  would take to satisfy all constraints simultaneously; testing it earlier
  with `maze_analyzer.py` instead of at the end would have caught issues
  sooner.

### Tools used
- Git / GitHub for version control and code review
- `flake8` and `mypy` for code quality and static typing checks
- `pytest` for unit tests (not submitted, used during development)
- An AI assistant (Claude), as described above, for README drafting and
  design discussions