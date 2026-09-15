import sys
from maze import MazeGenerator
from visualizer import menu_interativo


def main() -> None:
    """Lê a configuração, gera o labirinto e inicia o menu."""
    chaves_obrigatorias = [
        "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT",
    ]

    try:
        if len(sys.argv) < 2:
            raise ValueError("config.txt em falta")
        elif len(sys.argv) > 2:
            raise ValueError("Demasiados argumentos")
        caminho_config = sys.argv[1]

        with open(caminho_config, "r") as f:
            linhas = f.readlines()

        config: dict[str, str] = {}
        for linha in linhas:
            linha = linha.strip()
            if linha == "":
                continue
            if linha.startswith("#"):
                continue
            if "=" not in linha:
                raise ValueError(f"Linha inválida: {linha}. ! KEY=VALUE")

            chave, valor = linha.split("=", 1)
            chave = chave.strip()
            valor = valor.strip()

            if not chave or not valor:
                raise ValueError("A chave e o valor não podem estar vazios")

            if chave in config:
                raise ValueError(f"Chave repetida: {chave}")

            config[chave] = valor

        for chave in chaves_obrigatorias:
            if chave not in config:
                raise KeyError(f"Falta {chave} no ficheiro {sys.argv[1]}")

        width = int(config["WIDTH"])
        height = int(config["HEIGHT"])

        parts = config["ENTRY"].split(",")

        if len(parts) != 2:
            raise ValueError("ENTRY deve ter o formato x,y")

        entrada = (int(parts[0]), int(parts[1]))

        parts1 = config["EXIT"].split(",")

        if len(parts1) != 2:
            raise ValueError("EXIT deve ter o formato x,y")

        saida = (int(parts1[0]), int(parts1[1]))

        if config["PERFECT"] not in ("True", "False"):
            raise ValueError("PERFECT deve ser True ou False")

        perfeito = config["PERFECT"] == "True"

        seed = None
        if "SEED" in config:
            seed = int(config["SEED"])

        def criar_maze() -> MazeGenerator:
            """Cria e gera um novo maze de acordo com o config atual."""
            novo = MazeGenerator(
                width=width, height=height,
                entry=entrada, exit=saida, seed=seed,
            )

            novo.generate(perfect=perfeito)

            if not perfeito:
                novo.make_pacman_board()

            digitos = "0123456789ABCDEF"
            linhas_output = []

            for linha_maze in novo.walls:
                linha_hex = "".join(digitos[num] for num in linha_maze)
                linhas_output.append(linha_hex)

            caminho = novo.shortest_path()

            with open(config["OUTPUT_FILE"], "w") as f_out:
                for linha in linhas_output:
                    f_out.write(linha + "\n")
                f_out.write("\n")
                f_out.write(f"{novo.entry[0]},{novo.entry[1]}\n")
                f_out.write(f"{novo.exit[0]},{novo.exit[1]}\n")
                f_out.write("".join(caminho) + "\n")

            return novo

        g = criar_maze()

        menu_interativo(g, criar_maze)

    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
