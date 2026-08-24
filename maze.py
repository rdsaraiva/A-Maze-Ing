import random
from collections import deque


class MazeGenerator:
    """Gera um labirinto perfeito numa grelha e encontra o caminho mais curto.

    Utiliza o algoritmo de Depth-First Search (DFS) para remover paredes
    e gerar o labirinto, e Breadth-First Search (BFS) para resolver o caminho
    entre a entrada e a saída.

    Attributes:
        width (int): Largura do labirinto (número de colunas).
        height (int): Altura do labirinto (número de linhas).
        entry (tuple[int, int]): Coordenadas (x, y) do ponto de entrada.
        exit (tuple[int, int]): Coordenadas (x, y) do ponto de saída.
        seed (int | None): Semente para o gerador de números aleatórios.
        walls (list[list[int]]): Matriz representando o estado das paredes.
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
        seed: int | None = None,
    ) -> None:
        """Inicializa as dimensões, pontos de entrada/saída e valida os dados.

        Args:
            width: Largura do labirinto (deve ser > 0).
            height: Altura do labirinto (deve ser > 0).
            entry: Tuplo (x, y) com as coordenadas de entrada.
            exit: Tuplo (x, y) com as coordenadas de saída.
            seed: Semente opcional para reprodutibilidade.

        Raises:
            ValueError: Se a largura ou altura forem <= 0, se as coordenadas
                estiverem fora dos limites do labirinto, ou se a entrada e saída
                forem no mesmo local.
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.seed = seed

        if width <= 0:
            raise ValueError("width tem que ser positivo")

        if height <= 0:
            raise ValueError("height tem que ser positiva")

        if entry[0] >= width or entry[0] < 0:
            raise ValueError("coordenadas tem que ser validas")

        if entry[1] >= height or entry[1] < 0:
            raise ValueError("coordenadas tem que ser validas")

        if exit[0] >= width or exit[0] < 0:
            raise ValueError("coordenadas tem que ser validas")

        if exit[1] >= height or exit[1] < 0:
            raise ValueError("coordenadas tem que ser validas")

        if entry == exit:
            raise ValueError("não podes entrar na maze no sitío que sais")

        self.walls = [[15] * width for _ in range(height)]

    def generate(self) -> None:
        """Gera a estrutura de caminhos do labirinto modificando as paredes.

        Aplica o algoritmo Randomized Depth-First Search (com backtracking)
        para derrubar paredes a partir do ponto de entrada até cobrir a grelha.

        Raises:
            RuntimeError: Se após a geração existir alguma célula inacessível
                (não visitada).
        """
        visited = [[False] * self.width for _ in range(self.height)]

        DELTA = {
            "N": (0, -1),
            "E": (1, 0),
            "S": (0, 1),
            "W": (-1, 0),
        }

        BIT = {
            "N": 0b0001,
            "E": 0b0010,
            "S": 0b0100,
            "W": 0b1000,
        }

        OPOSTO = {
            "N": "S",
            "E": "W",
            "S": "N",
            "W": "E",
        }

        visited[self.entry[1]][self.entry[0]] = True
        rng = random.Random(self.seed)
        stack = [self.entry]
        while stack:
            x, y = stack[-1]
            candidatos = []
            for direcao, (dx, dy) in DELTA.items():
                nx = x + dx
                ny = y + dy
                inside_maze = 0 <= nx < self.width and 0 <= ny < self.height
                if inside_maze and not visited[ny][nx]:
                    candidatos.append((direcao, nx, ny))
            if candidatos:
                direcao, nx, ny = rng.choice(candidatos)
                self.walls[y][x] &= ~BIT[direcao]
                self.walls[ny][nx] &= ~BIT[OPOSTO[direcao]]
                visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                stack.pop()

        for y in range(self.height):
            for x in range(self.width):
                if not visited[y][x]:
                    raise RuntimeError(
                        f"As coordenadas x{x} & y{y} não foram visitadas"
                    )

    def shortest_path(self) -> list[str]:
        """Calcula a rota mais curta do ponto de entrada ao ponto de saída.

        Utiliza o algoritmo Breadth-First Search (BFS) para navegar
        pelas células cujas paredes foram removidas.

        Returns:
            list[str]: Uma lista de direções contendo as letras ('N', 'E',
            'S', 'W') que representam os passos do caminho até à saída.
        """
        fila = deque([self.entry])
        visto = {self.entry}
        veio_de = {}

        DELTA = {
            "N": (0, -1),
            "E": (1, 0),
            "S": (0, 1),
            "W": (-1, 0),
        }
        BIT = {
            "N": 0b0001,
            "E": 0b0010,
            "S": 0b0100,
            "W": 0b1000,
        }

        while fila:
            x, y = fila.popleft()
            if (x, y) == self.exit:
                break
            for direcao, (dx, dy) in DELTA.items():
                nx, ny = x + dx, y + dy
                inside = 0 <= nx < self.width and 0 <= ny < self.height
                if not inside:
                    continue
                if (nx, ny) in visto:
                    continue
                parede_aberta = (self.walls[y][x] & BIT[direcao]) == 0
                if not parede_aberta:
                    continue
                visto.add((nx, ny))
                veio_de[(nx, ny)] = ((x, y), direcao)
                fila.append((nx, ny))

        atual = self.exit
        caminho = []
        while atual != self.entry:
            anterior, direcao = veio_de[atual]
            caminho.append(direcao)
            atual = anterior
        caminho.reverse()
        return caminho
