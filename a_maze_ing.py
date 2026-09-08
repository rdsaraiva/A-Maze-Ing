import sys
from maze import MazeGenerator
from visualizer import menu_interativo


def main():
    chaves_obrigatorias = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]

    try:
        if len(sys.argv) < 2:
            raise ValueError("config.txt em falta")
        caminho_config = sys.argv[1]

        with open(caminho_config, "r") as f:
            linhas = f.readlines()

        config = {}
        for linha in linhas:
            linha = linha.strip()
            if linha == "":
                continue
            if linha.startswith("#"):
                continue
            chave, valor = linha.split("=")
            config[chave] = valor

        for chave in chaves_obrigatorias:
            if chave not in config:
                raise KeyError(f"Falta {chave} no config.txt")

        width = int(config["WIDTH"])
        height = int(config["HEIGHT"])

        parts = config["ENTRY"].split(",")
        x = int(parts[0])
        y = int(parts[1])
        entrada = (x, y)

        parts1 = config["EXIT"].split(",")
        x = int(parts1[0])
        y = int(parts1[1])
        saida = (x, y)

        perfeito = config["PERFECT"] == "True"

        # SEED é opcional: se não vier no config, fica None (aleatório).
        seed = None
        if "SEED" in config:
            seed = int(config["SEED"])

        def criar_maze():
            """Cria e gera um novo maze de acordo com o config atual."""
            novo = MazeGenerator(width=width, height=height, entry=entrada, exit=saida, seed=seed)
            novo.generate(perfect=perfeito)
            if not perfeito:
                novo.make_pacman_board()
            return novo

        g = criar_maze()

        digitos = "0123456789ABCDEF"
        linhas_output = []

        for linha_maze in g.walls:
            linha_hex = "".join(digitos[num] for num in linha_maze)
            linhas_output.append(linha_hex)

        caminho = g.shortest_path()

        # Escrever o ficheiro de output no formato pedido pelo enunciado:
        # paredes em hex, linha vazia, entrada, saída, caminho mais curto.
        with open(config["OUTPUT_FILE"], "w") as f_out:
            for linha in linhas_output:
                f_out.write(linha + "\n")
            f_out.write("\n")
            f_out.write(f"{entrada[0]},{entrada[1]}\n")
            f_out.write(f"{saida[0]},{saida[1]}\n")
            f_out.write("".join(caminho) + "\n")

        for linha in linhas_output:
            print(linha)

        # Mostrar o labirinto e o menu interativo (regenerar, mostrar/ocultar
        # caminho, mudar cores).
        menu_interativo(g, criar_maze)

    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
