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
        self.blocked_cells: set[tuple[int, int]] = set()

    def _livres_conectados(
        self,
        bloqueadas: set[tuple[int, int]],
    ) -> bool:
        """Verifica se todas as células fora do 42 continuam conectadas."""

        if self.entry in bloqueadas:
            return False

        visitadas = {self.entry}
        stack = [self.entry]

        direcoes = (
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, 0),
        )

        while stack:
            x, y = stack.pop()

            for dx, dy in direcoes:
                nx = x + dx
                ny = y + dy

                if not (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                ):
                    continue

                if (nx, ny) in bloqueadas:
                    continue

                if (nx, ny) in visitadas:
                    continue

                visitadas.add((nx, ny))
                stack.append((nx, ny))

        total_livres = (
            self.width * self.height
            - len(bloqueadas)
        )

        return len(visitadas) == total_livres

    def _criar_42(self, perfect: bool) -> bool:
        """Procura uma posição válida para o 42."""

        padrao = (
            "#---###",
            "#-----#",
            "###-###",
            "--#-#--",
            "--#-###",
        )

        altura_padrao = len(padrao)
        largura_padrao = len(padrao[0])

        self.blocked_cells.clear()

        if (
            self.width < largura_padrao
            or self.height < altura_padrao
        ):
            return False

        # Guardamos apenas as posições relativas dos '#'.
        bloqueios_relativos: list[tuple[int, int]] = [
            (dx, dy)
            for dy, linha in enumerate(padrao)
            for dx, valor in enumerate(linha)
            if valor == "#"
        ]

        protegidas = {
            self.entry,
            self.exit,
        }

        especiais: set[tuple[int, int]] = set()

        if not perfect:
            cantos = {
                (0, 0),
                (self.width - 1, 0),
                (0, self.height - 1),
                (self.width - 1, self.height - 1),
            }

            centro = {
                (
                    self.width // 2,
                    self.height // 2,
                )
            }

            especiais = cantos | centro

            protegidas.update(especiais)

        max_x = self.width - largura_padrao + 1
        max_y = self.height - altura_padrao + 1

        centro_padrao_x = (largura_padrao - 1) / 2
        centro_padrao_y = (altura_padrao - 1) / 2

        centro_maze_x = (self.width - 1) / 2
        centro_maze_y = (self.height - 1) / 2

        # Todas as posições onde o padrão cabe.
        posicoes: list[tuple[int, int]] = [
            (inicio_x, inicio_y)
            for inicio_y in range(max_y)
            for inicio_x in range(max_x)
        ]

        # Testamos primeiro as posições mais próximas do centro.
        posicoes.sort(
            key=lambda pos: (
                abs(
                    (pos[0] + centro_padrao_x)
                    - centro_maze_x
                )
                + abs(
                    (pos[1] + centro_padrao_y)
                    - centro_maze_y
                ),
                pos[1],
                pos[0],
            )
        )

        direcoes = (
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, 0),
        )

        for inicio_x, inicio_y in posicoes:

            bloqueadas = {
                (
                    inicio_x + dx,
                    inicio_y + dy,
                )
                for dx, dy in bloqueios_relativos
            }

            # Não pode ocupar ENTRY, EXIT,
            # cantos ou centro.
            if bloqueadas & protegidas:
                continue

            # No modo Pac-Man os cantos e centro
            # precisam de pelo menos dois vizinhos livres.
            if not perfect:
                especiais_validos = True

                for x, y in especiais:
                    vizinhos_livres = 0

                    for dx, dy in direcoes:
                        nx = x + dx
                        ny = y + dy

                        inside = (
                            0 <= nx < self.width
                            and 0 <= ny < self.height
                        )

                        if not inside:
                            continue

                        if (nx, ny) in bloqueadas:
                            continue

                        vizinhos_livres += 1

                    if vizinhos_livres < 2:
                        especiais_validos = False
                        break

                if not especiais_validos:
                    continue

            if not self._livres_conectados(bloqueadas):
                continue

            # Encontrámos a melhor posição válida.
            self.blocked_cells = bloqueadas

            return True

        return False

    def generate(self, perfect: bool = True) -> None:
        """Gera a estrutura de caminhos do labirinto modificando as paredes.

        Aplica o algoritmo Randomized Depth-First Search (com backtracking)
        para derrubar paredes a partir do ponto de entrada até cobrir a grelha.

        Raises:
            RuntimeError: Se após a geração existir alguma célula inacessível
                (não visitada).
        """
        criou_42 = self._criar_42(perfect)

        if not criou_42:
            print(
                "Erro: dimensões/posição do maze "
                "não permitem inserir o padrão 42"
            )
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
                if (
                    inside_maze
                    and (nx, ny) not in self.blocked_cells
                        and not visited[ny][nx]):
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
                if (x, y) in self.blocked_cells:
                    continue
                if not visited[y][x]:
                    raise RuntimeError(
                        f"As coordenadas x{x} & y{y} "
                        "não foram visitadas"
                    )

    def _numero_saidas(self, x: int, y: int) -> int:
        """Conta quantas passagens abertas existem numa célula."""

        if (x, y) in self.blocked_cells:
            return 0

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

        total = 0

        for direcao, (dx, dy) in DELTA.items():
            nx = x + dx
            ny = y + dy

            inside = 0 <= nx < self.width and 0 <= ny < self.height

            if not inside:
                continue

            parede_aberta = (self.walls[y][x] & BIT[direcao]) == 0

            if parede_aberta:
                total += 1

        return total

    def _paredes_fechadas(self, x: int, y: int):
        """Devolve as paredes internas que ainda podem ser abertas."""

        if (x, y) in self.blocked_cells:
            return []

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

        paredes = []

        for direcao, (dx, dy) in DELTA.items():
            nx = x + dx
            ny = y + dy

            inside = 0 <= nx < self.width and 0 <= ny < self.height

            if not inside:
                continue

            if (nx, ny) in self.blocked_cells:
                continue

            parede_fechada = (self.walls[y][x] & BIT[direcao]) != 0

            if parede_fechada:
                paredes.append((direcao, nx, ny))

        return paredes

    def _abrir_parede(self, x: int, y: int, direcao: str) -> bool:
        """Abre uma parede e a parede oposta da célula vizinha."""

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

        dx, dy = DELTA[direcao]

        nx = x + dx
        ny = y + dy

        inside = 0 <= nx < self.width and 0 <= ny < self.height

        if not inside:
            return False

        if (x, y) in self.blocked_cells:
            return False

        if (nx, ny) in self.blocked_cells:
            return False

        # A parede já estava aberta.
        if (self.walls[y][x] & BIT[direcao]) == 0:
            return False

        self.walls[y][x] &= ~BIT[direcao]
        self.walls[ny][nx] &= ~BIT[OPOSTO[direcao]]

        return True

    def make_pacman_board(self) -> None:
        """Transforma o perfect maze num tabuleiro adequado a Pac-Man."""

        # Número máximo de ciclos independentes possíveis numa grelha.
        if (self.width - 1) * (self.height - 1) < 2:
            raise ValueError(
                "Dimensões demasiado pequenas "
                "para criar dois ciclos independentes"
            )

        rng = random.Random(self.seed)

        # Como generate() cria uma árvore, cada nova parede aberta
        # acrescenta exatamente um ciclo independente.
        extra_edges = 0

        # Cantos e centro devem ser corredores
        especiais = {
            (0, 0),
            (self.width - 1, 0),
            (0, self.height - 1),
            (self.width - 1, self.height - 1),
        }

        centro = (
            self.width // 2,
            self.height // 2,
        )

        especiais.add(centro)

        for x, y in especiais:

            # Uma célula com apenas uma saída é um dead-end.
            # Queremos pelo menos duas saídas.
            while self._numero_saidas(x, y) < 2:

                fechadas = self._paredes_fechadas(x, y)

                if not fechadas:
                    break

                # Se for possível ligar dois dead-ends ao mesmo tempo.
                preferidas = [
                    parede
                    for parede in fechadas
                    if self._numero_saidas(parede[1], parede[2]) == 1
                ]

                direcao, _, _ = rng.choice(preferidas or fechadas)

                if self._abrir_parede(x, y, direcao):
                    extra_edges += 1

        # Eliminar dead-ends
        while True:

            becos = [
                (x, y)
                for y in range(self.height)
                for x in range(self.width)
                if self._numero_saidas(x, y) == 1
            ]

            if not becos:
                break

            rng.shuffle(becos)

            abriu_alguma = False

            for x, y in becos:

                # Pode já ter deixado de ser dead-end porque uma
                # célula processada anteriormente se ligou a ela.
                if self._numero_saidas(x, y) != 1:
                    continue

                fechadas = self._paredes_fechadas(x, y)

                if not fechadas:
                    continue

                # Preferimos ligar a outro dead-end porque uma única
                # parede pode resolver dois becos simultaneamente.
                preferidas = [
                    parede
                    for parede in fechadas
                    if self._numero_saidas(parede[1], parede[2]) == 1
                ]

                direcao, _, _ = rng.choice(preferidas or fechadas)

                if self._abrir_parede(x, y, direcao):
                    extra_edges += 1
                    abriu_alguma = True

            if not abriu_alguma:
                break

        # Garantir pelo menos dois ciclos independentes

        while extra_edges < 2:

            candidatas = []

            for y in range(self.height):
                for x in range(self.width):

                    # Só E e S para não contar a mesma parede duas vezes.
                    for direcao, nx, ny in self._paredes_fechadas(x, y):

                        if direcao in ("E", "S"):
                            candidatas.append((x, y, direcao))

            if not candidatas:
                raise RuntimeError(
                    "Não foi possível criar dois ciclos independentes"
                )

            x, y, direcao = rng.choice(candidatas)

            if self._abrir_parede(x, y, direcao):
                extra_edges += 1

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
