import sys
from typing import List, Tuple, Set

PALETAS = [
    {
        "nome": "Cyberpunk 42",
        "parede": "\033[38;2;240;160;60m██\033[0m",
        "caminho": "\033[38;2;80;220;240m░░\033[0m",
        "entrada": "\033[38;2;160;70;255m██\033[0m",
        "saida": "\033[38;2;255;50;100m██\033[0m",
        "p42": "\033[38;2;57;255;20m█░\033[0m",
    },
    {
        "nome": "Matrix Terminal",
        "parede": "\033[38;2;0;230;118m██\033[0m",
        "caminho": "\033[38;2;186;104;200m░░\033[0m",
        "entrada": "\033[38;2;255;255;255m██\033[0m",
        "saida": "\033[38;2;255;23;68m██\033[0m",
        "p42": "\033[38;2;57;255;20m█░\033[0m",
    },
    {
        "nome": "Synthwave Sunset",
        "parede": "\033[38;2;255;0;127m██\033[0m",
        "caminho": "\033[38;2;255;234;0m░░\033[0m",
        "entrada": "\033[38;2;0;229;255m██\033[0m",
        "saida": "\033[38;2;255;45;85m██\033[0m",
        "p42": "\033[38;2;57;255;20m█░\033[0m",
    },
]


def obter_posicoes_caminho(
    entry: Tuple[int, int],
    caminho_direcoes: List[str],
) -> Set[Tuple[int, int]]:
    posicoes = set()
    x, y = entry
    posicoes.add((x, y))
    DELTA = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
    for d in caminho_direcoes:
        dx, dy = DELTA[d]
        x += dx
        y += dy
        posicoes.add((x, y))
    return posicoes


def desenhar_labirinto(
    maze,
    mostrar_caminho: bool = True,
    indice_paleta: int = 0,
) -> None:
    # Passo 1: Limpar o terminal
    sys.stdout.write("\033[H\033[2J\033[3J")
    sys.stdout.flush()

    paleta = PALETAS[indice_paleta % len(PALETAS)]
    p_wall = paleta["parede"]

    # Passo 2: Mapear o caminho mais curto
    caminho_set = set()
    if mostrar_caminho:
        caminho_dirs = maze.shortest_path()
        caminho_set = obter_posicoes_caminho(maze.entry, caminho_dirs)

    # Passo 3: Criar a matriz visual preenchida inicialmente só com paredes
    # Cada célula (x,y) ocupa 2 caracteres de largura e 2 de altura na
    # grelha final
    grelha_largura = maze.width * 2 + 1
    grelha_altura = maze.height * 2 + 1
    grelha = [
        [p_wall for _ in range(grelha_largura)]
        for _ in range(grelha_altura)
    ]

    # Passo 4: Escavar o interior das células e abrir as paredes
    for y in range(maze.height):
        for x in range(maze.width):
            célula = maze.walls[y][x]
            pos = (x, y)

            # Mapeamento de coordenadas (x, y) do labirinto para a grelha
            # de texto
            gx = x * 2 + 1
            gy = y * 2 + 1

            # 4.1. Definir o centro da célula
            if pos == maze.entry:
                grelha[gy][gx] = paleta["entrada"]
            elif pos == maze.exit:
                grelha[gy][gx] = paleta["saida"]
            elif célula == 15:
                grelha[gy][gx] = paleta["p42"]
            elif mostrar_caminho and pos in caminho_set:
                grelha[gy][gx] = paleta["caminho"]
            else:
                grelha[gy][gx] = "  "

            # 4.2. Abrir parede Este se o Bit 1 (valor 2) for 0
            if (célula & 2) == 0:
                grelha[gy][gx + 1] = "  "

            # 4.3. Abrir parede Sul se o Bit 2 (valor 4) for 0
            if (célula & 4) == 0:
                grelha[gy + 1][gx] = "  "

    # Passo 5: Converter a matriz de texto em strings e imprimir
    output = "\n".join("".join(linha) for linha in grelha)
    print(output)


def menu_interativo(maze, gerador_callback) -> None:
    mostrar_caminho = True
    indice_paleta = 0

    while True:
        desenhar_labirinto(maze, mostrar_caminho, indice_paleta)
        paleta = PALETAS[indice_paleta % len(PALETAS)]
        nome_tema = paleta["nome"]
        legenda = (
            f"Entrada: {paleta['entrada']}  "
            f"Saída: {paleta['saida']}  "
            f"Caminho: {paleta['caminho']}"
        )

        print(
            f"\n\033[1m=== A-Maze-ing ===\033[0m "
            f"[Tema: \033[36m{nome_tema}\033[0m]"
        )
        print(f"Legenda: {legenda}\n")
        print("1. Regenerar novo labirinto")
        print("2. Mostrar/Ocultar caminho mais curto")
        print("3. Rotacionar cores das paredes")
        print("4. Sair")

        opcao = input("\nEscolha (1-4): ").strip()

        if opcao == "1":
            maze = gerador_callback()
        elif opcao == "2":
            mostrar_caminho = not mostrar_caminho
        elif opcao == "3":
            indice_paleta += 1
        elif opcao == "4":
            print("Até à próxima!")
            break
        else:
            input("Opção inválida! Pressiona Enter para tentar novamente...")
