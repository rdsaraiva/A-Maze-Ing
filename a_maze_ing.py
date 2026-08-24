import sys
from maze import MazeGenerator


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

        g = MazeGenerator(width=width, height=height, entry=entrada, exit=saida)
        g.generate()

        digitos = "0123456789ABCDEF"
        linhas_output = []

        for linha_maze in g.walls:
            linha_hex = "".join(digitos[num] for num in linha_maze)
            linhas_output.append(linha_hex)

        for linha in linhas_output:
            print(linha)

    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()