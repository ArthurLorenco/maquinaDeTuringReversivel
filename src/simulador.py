import re
import sys


BLANK = "B"
STEP_LIMIT = 10_000_000
TRANSITION_RE = re.compile(r"\((\d+),(.+)\)=\((\d+),(.+),([LRSN])\)$")


def ler_descricao():
    tokens = sys.stdin.read().split()
    if len(tokens) < 4:
        raise ValueError("Entrada invalida: cabecalho ausente.")

    estados, alfabeto_entrada, alfabeto_fita, quantidade = map(int, tokens[:4])
    indice = 4 + estados + alfabeto_entrada + alfabeto_fita
    if len(tokens) < indice + quantidade:
        raise ValueError("Entrada invalida: transicoes ausentes.")

    transicoes = []
    for numero in range(quantidade):
        texto = tokens[indice + numero]
        match = TRANSITION_RE.fullmatch(texto)
        if not match:
            raise ValueError(f"Transicao invalida na posicao {numero + 1}: {texto}")
        origem, lido, destino, escrito, movimento = match.groups()
        if len(lido) != 1 or len(escrito) != 1:
            raise ValueError(f"Simbolo invalido na transicao: {texto}")
        transicoes.append((int(origem), lido, int(destino), escrito,
                           "S" if movimento == "N" else movimento))

    entrada = tokens[indice + quantidade] if len(tokens) > indice + quantidade else ""
    return estados, transicoes, entrada


def simbolo_da_fita(fita, posicao):
    return fita.get(posicao, BLANK)


def texto_da_fita(fita):
    usadas = sorted(posicao for posicao, simbolo in fita.items() if simbolo != BLANK)
    if not usadas:
        return "vazia"
    return "".join(fita[posicao] for posicao in usadas)


def construir_quadruplas(transicoes, quantidade_estados):
    # Bennett quebra toda quintupla (leitura+escrita+deslocamento no mesmo passo)
    # em 2 quadruplas: uma so de leitura/escrita, outra so de deslocamento,
    # ligadas por um estado intermediario novo (exclusivo dessa transicao).
    quadruplas = []

    print("Quintuplas convertidas em quadruplas:")
    for indice, (origem, lido, destino, escrito, movimento) in enumerate(transicoes, start=1):
        intermediario = quantidade_estados + indice

        quadruplas.append({
            "tipo": "RW",
            "indice": indice,
            "estado": origem,
            "lido": lido,
            "escrito": escrito,
            "proximo_estado": intermediario,
        })
        quadruplas.append({
            "tipo": "MOVE",
            "indice": indice,
            "estado": intermediario,
            "movimento": movimento,
            "proximo_estado": destino,
        })

        print(f"  T{indice}: (q{origem},'{lido}')=(q{destino},'{escrito}',{movimento})"
              f"  ->  (q{origem},'{lido}')=('{escrito}',q{intermediario})"
              f"  +  (q{intermediario},/)=({movimento},q{destino})")

    return quadruplas


def fase1_simulacao(quadruplas, entrada, quantidade_estados):
    leitura_escrita = {(q["estado"], q["lido"]): q for q in quadruplas if q["tipo"] == "RW"}
    deslocamento = {q["estado"]: q for q in quadruplas if q["tipo"] == "MOVE"}

    fita = {posicao: simbolo for posicao, simbolo in enumerate(entrada)}
    historico = []
    estado = 1
    cabeca = 0
    passo = 0

    print(f"\nFase 1: simulacao com quadruplas (entrada: {entrada or '(vazia)'})")

    while estado != quantidade_estados:
        if passo >= STEP_LIMIT:
            print(f"Erro: limite de {STEP_LIMIT} passos excedido.", file=sys.stderr)
            return None

        if estado in deslocamento:
            quad = deslocamento[estado]
            registro = {
                "passo": passo + 1,
                "tipo": "MOVE",
                "estado_anterior": estado,
                "movimento": quad["movimento"],
            }
            historico.append(registro)

            if quad["movimento"] == "L":
                cabeca -= 1
            elif quad["movimento"] == "R":
                cabeca += 1
            estado = quad["proximo_estado"]

            print(f"  {registro['passo']:>3}: T{quad['indice']} deslocamento: "
                  f"q{registro['estado_anterior']}, {quad['movimento']}, q{estado}")
        else:
            lido = simbolo_da_fita(fita, cabeca)
            quad = leitura_escrita.get((estado, lido))
            if quad is None:
                print(f"Erro: nao ha transicao para estado {estado} e simbolo '{lido}'.", file=sys.stderr)
                return None

            registro = {
                "passo": passo + 1,
                "tipo": "RW",
                "estado_anterior": estado,
                "cabeca": cabeca,
                "simbolo_anterior": lido,
            }
            historico.append(registro)

            fita[cabeca] = quad["escrito"]
            estado = quad["proximo_estado"]

            print(f"  {registro['passo']:>3}: T{quad['indice']} leitura/escrita: "
                  f"q{registro['estado_anterior']}, '{lido}' -> '{quad['escrito']}', q{estado}")

        passo += 1

    print(f"Fita 1: {texto_da_fita(fita)}")
    print(f"Passos no historico: {len(historico)}")

    return fita, historico, estado


def fase2_copia(fita):
    # tem que copiar antes do retrace: a fase 3 desfaz a fita 1 ate ela virar
    # a entrada de novo, entao sem essa copia a saida se perderia junto
    print("\nFase 2: copia do resultado pra fita 3")

    fita_output = {}
    posicoes_fita1 = sorted(p for p, s in fita.items() if s != BLANK)

    for i, pos in enumerate(posicoes_fita1):
        simbolo = fita[pos]
        fita_output[i] = simbolo
        print(f"  Copiando simbolo '{simbolo}' da Fita 1[{pos}] para Fita 3[{i}]")

    print(f"Fita 3: {texto_da_fita(fita_output)}")
    return fita_output


def fase3_retrace(fita, historico, estado):
    print("\nFase 3: retrace, desfazendo os passos da fase 1")

    # desfazer na ordem inversa garante que, se uma posicao foi escrita
    # mais de uma vez, ela volta ao valor de ANTES do primeiro passo
    # que a tocou (tipo uma pilha, ultimo a entrar, primeiro a sair)
    for registro in reversed(historico):
        estado = registro["estado_anterior"]

        if registro["tipo"] == "RW":
            fita[registro["cabeca"]] = registro["simbolo_anterior"]
            print(f"  Desfazendo passo {registro['passo']:>3}: Voltou para q{estado}, "
                  f"Restaurou '{registro['simbolo_anterior']}' em Fita 1[{registro['cabeca']}]")
        else:
            print(f"  Desfazendo passo {registro['passo']:>3}: Voltou para q{estado} (deslocamento desfeito)")

    # Limpa o histórico após o Retrace
    historico.clear()
    return estado


def main():
    try:
        quantidade_estados, transicoes, entrada = ler_descricao()
    except ValueError as erro:
        print(erro, file=sys.stderr)
        return 1

    quadruplas = construir_quadruplas(transicoes, quantidade_estados)

    resultado = fase1_simulacao(quadruplas, entrada, quantidade_estados)
    if resultado is None:
        return 1
    fita, historico, estado = resultado

    fita_output = fase2_copia(fita)
    estado = fase3_retrace(fita, historico, estado)

    print("\nResultado final:")
    print(f"Estado: q{estado}")
    print(f"Fita 1 (entrada reconstruida): {texto_da_fita(fita)}")
    print("Fita 2 (historico): vazia")
    print(f"Fita 3 (saida): {texto_da_fita(fita_output)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
