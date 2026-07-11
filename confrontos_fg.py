import json
import random
from itertools import combinations

# ==========================================================
# Carregamento dos arquivos
# ==========================================================

def carregar_ratos(arquivo="ratos.json"):
    """
    Carrega todos os ratos e retorna um dicionário indexado pelo nome.
    """
    with open(arquivo, "r", encoding="utf-8") as f:
        dados = json.load(f)

    return {rato["nome"]: rato for rato in dados}


def carregar_grupos(arquivo="fase_de_grupos.json"):
    """
    Carrega os grupos sorteados.
    """
    with open(arquivo, "r", encoding="utf-8") as f:
        return json.load(f)


# ==========================================================
# Tabela de Pontuação
# ==========================================================

def criar_tabela_pontos(grupos):
    """
    Cria a tabela inicial de classificação.
    """
    tabela = {}
    for grupo, competidores in grupos.items():
        tabela[grupo] = {
            nome: {"pts": 0, "vitorias": 0, "derrotas": 0} 
            for nome in competidores
        }
    return tabela


# ==========================================================
# Confrontos
# ==========================================================

def gerar_confrontos(grupos):
    """
    Gera todos os confrontos da fase de grupos sem repetir A×B e B×A.
    """
    confrontos = {}
    for grupo, competidores in grupos.items():
        confrontos[grupo] = list(combinations(competidores, 2))
    return confrontos


# ==========================================================
# Iniciativa
# ==========================================================

def calcular_iniciativa(rato):
    """
    Calcula a iniciativa de um rato.
    Fórmula: velocidade * precisão
    """
    atributos = rato["atributos"]
    velocidade = atributos["velocidade"]
    precisao = atributos["acerto"] / 100

    return random.uniform(0, velocidade * precisao)


# ==========================================================
# Dano
# ==========================================================

def calcular_dano(atacante, defensor):
    """
    Calcula o dano causado pelo atacante e retorna os dados do turno.
    """
    atk = atacante["atributos"]
    dfs = defensor["atributos"]

    forca = atk["forca"]
    inteligencia = atk["inteligencia"]
    acerto = atk["acerto"] / 100
    resistencia_max = dfs["resistencia"]

    base = round(((forca+inteligencia) - round(abs(forca - inteligencia) / 2)) * acerto)
    resistencia_sorteada = random.randint(1, max(1, resistencia_max))
    dano = max(1, base - resistencia_sorteada)

    return {
        "forca": forca,
        "inteligencia": inteligencia,
        "acerto": atk["acerto"],
        "base": base,
        "resistencia_inimigo": resistencia_max,
        "resistencia_sorteada": resistencia_sorteada,
        "dano": dano
    }


# ==========================================================
# Executa um turno
# ==========================================================

def executar_turno(atacante, defensor):
    """
    Executa um único ataque e modifica a vida do defensor.
    """
    info = calcular_dano(atacante, defensor)
    vida_antes = defensor["vida"]
    
    defensor["vida"] = max(0, defensor["vida"] - info["dano"])

    return {
        "atacante": atacante["nome"],
        "defensor": defensor["nome"],
        "vida_atacante": atacante["vida"],
        "vida_defensor_antes": vida_antes,
        "formula": {
            "forca": info["forca"],
            "inteligencia": info["inteligencia"],
            "acerto": info["acerto"],
            "base": info["base"],
            "resistencia_inimigo": info["resistencia_inimigo"],
            "resistencia_sorteada": info["resistencia_sorteada"]
        },
        "dano": info["dano"],
        "vida_defensor_depois": defensor["vida"]
    }


# ==========================================================
# Combate completo
# ==========================================================

def executar_combate(rato1, rato2, grupo):
    """
    Executa um combate inteiro entre dois ratos.
    """
    competidor1 = {
        "nome": rato1["nome"],
        "vida": rato1["atributos"]["vida"],
        "atributos": rato1["atributos"]
    }

    competidor2 = {
        "nome": rato2["nome"],
        "vida": rato2["atributos"]["vida"],
        "atributos": rato2["atributos"]
    }

    iniciativa1 = calcular_iniciativa(rato1)
    iniciativa2 = calcular_iniciativa(rato2)

    if iniciativa1 >= iniciativa2:
        atacante, defensor = competidor1, competidor2
        primeiro = competidor1["nome"]
    else:
        atacante, defensor = competidor2, competidor1
        primeiro = competidor2["nome"]

    turnos = []
    numero_turno = 1

    while True:
        turno = executar_turno(atacante, defensor)
        turno["turno"] = numero_turno
        turnos.append(turno)

        if defensor["vida"] <= 0:
            vencedor = atacante["nome"]
            perdedor = defensor["nome"]
            break

        atacante, defensor = defensor, atacante
        numero_turno += 1

    return {
        "grupo": grupo,
        "competidores": [rato1["nome"], rato2["nome"]],
        "vencedor": vencedor,
        "perdedor": perdedor,
        "pontuacao": {
            vencedor: 2,
            perdedor: -1
        },
        "iniciativa": {
            rato1["nome"]: round(iniciativa1, 3),
            rato2["nome"]: round(iniciativa2, 3),
            "primeiro": primeiro
        },
        "turnos": turnos
    }


# ==========================================================
# Executa todos os confrontos de um grupo
# ==========================================================

def executar_grupo(nome_grupo, confrontos, ratos, tabela):
    """
    Executa todos os confrontos de um grupo e atualiza a tabela.
    """
    resultados = []

    for nome1, nome2 in confrontos:
        combate = executar_combate(ratos[nome1], ratos[nome2], nome_grupo)

        vencedor = combate["vencedor"]
        perdedor = combate["perdedor"]

        tabela[nome_grupo][vencedor]["pts"] += 2
        tabela[nome_grupo][vencedor]["vitorias"] += 1
        tabela[nome_grupo][perdedor]["pts"] -= 1
        tabela[nome_grupo][perdedor]["derrotas"] += 1

        resultados.append(combate)

    return resultados


# ==========================================================
# Salvamento
# ==========================================================

def salvar_resultado_confrontos(resultados, arquivo="resultado_confrontos.json"):
    """
    Salva todos os combates realizados no JSON.
    """
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)


def salvar_colocacoes(tabela, arquivo="colocacoes.json"):
    """
    Ordena cada grupo por Pontos, Vitórias e Derrotas e salva.
    """
    resultado = {}

    for grupo, competidores in tabela.items():
        ranking = sorted(
            competidores.items(),
            key=lambda x: (x[1]["pts"], x[1]["vitorias"], -x[1]["derrotas"]),
            reverse=True
        )

        classificacao = {}
        for posicao, (nome, dados) in enumerate(ranking, start=1):
            classificacao[f"{posicao}º"] = {
                "nome": nome,
                "pts": dados["pts"],
                "vitorias": dados["vitorias"],
                "derrotas": dados["derrotas"]
            }

        resultado[grupo] = classificacao

    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=4)


# ==========================================================
# Main
# ==========================================================

def main():
    ratos = carregar_ratos()
    grupos = carregar_grupos()
    tabela = criar_tabela_pontos(grupos)
    confrontos = gerar_confrontos(grupos)
    
    todos_os_resultados = []

    for grupo in grupos.keys():
        resultados = executar_grupo(grupo, confrontos[grupo], ratos, tabela)
        todos_os_resultados.extend(resultados)

    salvar_resultado_confrontos(todos_os_resultados)
    salvar_colocacoes(tabela)

    print("Fase de grupos concluída!")
    print("Arquivos gerados:")
    print(" - resultado_confrontos.json")
    print(" - colocacoes.json")


if __name__ == "__main__":
    main()