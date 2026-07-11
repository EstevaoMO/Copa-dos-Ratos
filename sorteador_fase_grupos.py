from itertools import combinations
from statistics import mean, pstdev
import json

def carregar_ratos(arquivo="ratos.json"):
    with open(arquivo, encoding="utf8") as f:
        return json.load(f)


def power_rating(rato):
    a = rato["atributos"]

    return (
        a["vida"] +
        a["resistencia"] +
        a["forca"] +
        a["inteligencia"] +
        a["velocidade"]
    ) / 5

def media_grupo(grupo):
    return mean(power_rating(r) for r in grupo)


def desvio_grupo(grupo):
    return pstdev(power_rating(r) for r in grupo)


def avaliar(A, B, C):
    medias = [
        media_grupo(A),
        media_grupo(B),
        media_grupo(C)
    ]

    desvios = [
        desvio_grupo(A),
        desvio_grupo(B),
        desvio_grupo(C)
    ]

    desvio_entre_grupos = pstdev(medias)
    score = desvio_entre_grupos + 0.2 * mean(desvios)

    return score


def melhor_sorteio(ratos):

    melhor_score = float("inf")
    melhor = None

    indices = range(len(ratos))

    for grupoA in combinations(indices, 5):
        restantes1 = list(set(indices) - set(grupoA))

        for grupoB in combinations(restantes1, 5):

            grupoC = tuple(set(restantes1) - set(grupoB))

            A = [ratos[i] for i in grupoA]
            B = [ratos[i] for i in grupoB]
            C = [ratos[i] for i in grupoC]

            score = avaliar(A, B, C)
            if score < melhor_score:
                melhor_score = score
                melhor = (
                    A,
                    B,
                    C
                )

    return melhor, melhor_score


def imprimir(nome, grupo):
    import os

    arquivo = "fase_de_grupos.json"
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
    else:
        dados = {}
    
    dados[f"grupo_{nome}"] = [
        rato["nome"] for rato in grupo
    ]

    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# -------------------------------------------------

def main():
    ratos = carregar_ratos()
    grupos, score = melhor_sorteio(ratos)
    A, B, C = grupos

    imprimir("A", A)
    imprimir("B", B)
    imprimir("C", C)

    print("\nScore:", round(score, 5))


if __name__ == "__main__":
    main()