*This project has been created as part of the 42 curriculum by dcarneir, roda-fon.*

# A-Maze-ing — This is the way

## Description

**A-Maze-ing** is a Python maze generator and visualizer. Given a simple text
configuration file, the program generates a maze — either a **perfect maze**
(exactly one path between entrance and exit, no loops) or a **Pac-Man-style
board** (fully connected, open corners and centre, at least two independent
routes, rare dead-ends) — writes it to an output file using a compact
hexadecimal wall encoding, and displays it in the terminal using Unicode
characters and ANSI colours.

The goal of the project is twofold:
- Explore classic maze-generation algorithms (recursive backtracker, Prim's,
  Kruskal's, etc.), randomness, and the graph-theory link between perfect
  mazes and spanning trees.
- Package the generation logic as a **reusable, pip-installable module**
  distributed as `mazegen`, exposing the `maze` module for use in future
  projects independently of the CLI and visualization code.

## Instructions

### Requirements
- Python 3.10+

### Installation
```bash
git clone <repo-url>
cd a-maze-ing
make install
```
`make install` installs the development tools listed in `requirements.txt`
using the current Python environment. It does not create or activate a
virtual environment.

The maze generator itself uses only the Python standard library.

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
| `make build` | Builds the reusable distribution and places the `.whl` and `.tar.gz` files at the repository root |


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
| `SEED` | Optional integer seed for reproducible generation | `SEED=42` | no |

With the same seed, configuration and implementation, generation produces
the same maze. The menu's regeneration option reuses the configured seed,
so it reproduces the same maze when `SEED` is provided.

If `SEED` is omitted, each generation uses a newly initialized random
generator and may produce a different maze.

A ready-to-use default configuration file, `config.txt`, is provided at the
root of the repository.

Any malformed line, missing mandatory key, out-of-bounds coordinate, or
otherwise impossible parameter combination is reported to the user with a
clear error message; the program never crashes on invalid input.

## Maze generation algorithm

**Algorithm chosen: randomized depth-first search with backtracking,
implemented using an explicit stack.**

Starting from a grid where every cell has all four walls closed, the
algorithm picks a starting cell, marks it as visited, and repeatedly moves
to a random unvisited neighbour, knocking down the wall between the current
cell and that neighbour as it goes. When a cell has no unvisited neighbour
left, the algorithm backtracks along the path it came from (hence the name)
until it finds a cell that still has an unvisited neighbour, and continues
from there. This carves a spanning tree of the grid: by construction there
is exactly one path between any two cells, which is exactly what the
`PERFECT=True` mode requires.

Before DFS starts, the generator reserves fully closed cells forming the
"42" pattern. It searches for a placement that preserves connectivity
between all remaining cells and avoids the entry and exit.

In non-perfect mode, the placement also protects the four corners and
the centre, keeping at least two available neighbouring cells for each.

To produce the `PERFECT=False` board, the program first generates the DFS
spanning tree and then calls `make_pacman_board()`:

- It opens additional passages at the corners and centre to give them
  at least two exits.
- It repeatedly attempts to remove dead-ends, preferring openings that
  connect two dead-ends at once.
- It ensures that at least two additional walls have been opened.
  Starting from a connected tree, each new passage adds one independent
  cycle.

The implementation does not perform an explicit check for fully open
3x3 areas.

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
dead-ends. The project does not implement multiple generation algorithms or
generation animation. The Pac-Man adaptation attempts to eliminate
dead-ends, but does not guarantee a zero-dead-end board for every
configuration.

## Reusable module

The reusable generation logic is implemented by the `MazeGenerator`
class in `maze.py`. It is independent of the configuration parser,
output writer and terminal visualizer.

The distribution is named `mazegen`, while the Python module is named
`maze`. After installation, import the class using:

```python
from maze import MazeGenerator
```

The code is distributed under the MIT license in `LICENSE.md`.

### Building the distribution

```bash
make build
```

This creates the following files at the repository root:

- `mazegen-1.0.0-py3-none-any.whl`
- `mazegen-1.0.0.tar.gz`

The build configuration is provided in `pyproject.toml`.
The README supplies the distribution description.

### Installing in another project

Inside the target project's virtual environment:

```bash
python -m pip install /path/to/mazegen-1.0.0-py3-none-any.whl
```

Replace `/path/to/` with the actual location of the wheel.

### Basic usage: perfect maze

```python
from maze import MazeGenerator

generator = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit=(19, 14),
    seed=42,
)

generator.generate(perfect=True)

grid = generator.walls
path = generator.shortest_path()

print("".join(path))
```

The constructor accepts the dimensions, entry, exit and optional seed.
The `perfect` argument belongs to `generate()`, not to the constructor.

`generate()` modifies the object and returns `None`.

### Non-perfect mode

```python
generator = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit=(19, 14),
    seed=42,
)

generator.generate(perfect=False)
generator.make_pacman_board()

grid = generator.walls
path = generator.shortest_path()
```

In this implementation, `generate(perfect=False)` prepares the pattern
placement for non-perfect mode and generates the DFS tree.
The separate call to `make_pacman_board()` opens additional passages.

### Accessing the result

- `generator.walls[y][x]` contains the wall value of cell `(x, y)`.
- Wall bits are North=1, East=2, South=4 and West=8.
- A set bit means a closed wall; a cleared bit means an open passage.
- `generator.blocked_cells` contains the coordinates reserved for the 42.
- `generator.shortest_path()` returns a list of directions: N, E, S or W.

Coordinates use `(x, y)`, with the origin at the top-left.
The matrix is indexed by `[y][x]`.

Create a new `MazeGenerator` instance for each new maze, as the CLI does.
The generator does not write output files or display the interactive menu;
those responsibilities belong to the main program and visualizer.

## Resources

- Wikipedia — "Maze generation algorithm"
- Jamis Buck, *Buckblog* — series of articles on maze generation algorithms
  (recursive backtracker, Prim's, Kruskal's)
- Course material and Wikipedia on spanning trees, to understand why a
  recursive backtracker produces a perfect maze
- Python official documentation for `random`, `collections.deque`,
  `typing` and file handling
- `mypy` and `flake8` documentation for the linting configuration


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
- An AI assistant (Claude), as described above, for README drafting and
  design discussions