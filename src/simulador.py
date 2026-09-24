#!/usr/bin/env python3
"""Simulador de Máquina de Turing Reversível de 3 Fitas (3 Estágios)."""

import re
import sys
from typing import List, Dict, Tuple, Any


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


def main():
    try:
        quantidade_estados, transicoes, entrada = ler_descricao()
    except ValueError as erro:
        print(erro, file=sys.stderr)
        return 1

    # Inicialização da Fita 1 (Input/Working)
    fita = {posicao: simbolo for posicao, simbolo in enumerate(entrada)}
    historico = []
    estado = 1
    cabeca = 0
    passo = 0

    print("=" * 70)
    print("FASE 1 — Simulacao Forward da MT Original (Fita 1 e Histórico)")
    print("=" * 70)
    print(f"Entrada: {entrada or '(vazia)'}")
    print("Passos:")

    while estado != quantidade_estados:
        lido = simbolo_da_fita(fita, cabeca)
        escolhida = None
        indice_transicao = None

        for indice, transicao in enumerate(transicoes, start=1):
            origem, simbolo_lido, destino, escrito, movimento = transicao
            if origem == estado and simbolo_lido == lido:
                escolhida = transicao
                indice_transicao = indice
                break

        if escolhida is None:
            print(f"Erro: nao ha transicao para estado {estado} e simbolo '{lido}'.", file=sys.stderr)
            return 1
        if passo >= STEP_LIMIT:
            print(f"Erro: limite de {STEP_LIMIT} passos excedido.", file=sys.stderr)
            return 1

        origem, simbolo_lido, destino, escrito, movimento = escolhida

        # Registro para histórico do Retrace
        registro = {
            "passo": passo + 1,
            "transicao": indice_transicao,
            "estado_anterior": estado,
            "cabeca_anterior": cabeca,
            "simbolo_anterior": lido,
            "simbolo_escrito": escrito,
            "estado_novo": destino,
            "movimento": movimento,
        }
        historico.append(registro)

        fita[cabeca] = escrito
        if movimento == "L":
            cabeca -= 1
        elif movimento == "R":
            cabeca += 1
        estado = destino
        passo += 1

        print(f"  {registro['passo']:>3}: T{indice_transicao}: "
              f"q{origem}, '{lido}' -> '{escrito}', {movimento}, q{destino}")

    print("\nFase 1 Concluída com Sucesso!")
    print(f"Estado final: {estado}")
    print(f"Conteudo Fita 1: {texto_da_fita(fita)}")
    print(f"Passos no historico: {len(historico)}")

    # =========================================================================
    # FASE 2 — Cópia do Resultado para a Fita 3 (Output Tape)
    # =========================================================================
    print("\n" + "=" * 70)
    print("FASE 2 — Copia da Saida (Fita 1 -> Fita 3)")
    print("=" * 70)

    fita_output = {}
    posicoes_fita1 = sorted(p for p, s in fita.items() if s != BLANK)

    for i, pos in enumerate(posicoes_fita1):
        simbolo = fita[pos]
        fita_output[i] = simbolo
        print(f"  Copiando simbolo '{simbolo}' da Fita 1[{pos}] para Fita 3[{i}]")

    print(f"\nFase 2 Concluida!")
    print(f"Conteudo Fita 3 (Output): {texto_da_fita(fita_output)}")

    # =========================================================================
    # FASE 3 — Retrace / Reversão das Operações
    # =========================================================================
    print("\n" + "=" * 70)
    print("FASE 3 — Retrace (Desfazendo passos para restaurar estado inicial)")
    print("=" * 70)

    pas_retrace = 0
    # Percorre o histórico na ordem inversa
    for registro in reversed(historico):
        pas_retrace += 1
        
        # Inverte o movimento realizado
        mov = registro["movimento"]
        if mov == "L":
            cabeca += 1
        elif mov == "R":
            cabeca -= 1

        # Restaura estado e conteúdo da Fita 1
        estado = registro["estado_anterior"]
        fita[registro["cabeca_anterior"]] = registro["simbolo_anterior"]

        print(f"  Desfazendo passo {registro['passo']:>3}: Voltou para q{estado}, "
              f"Restaurou '{registro['simbolo_anterior']}' em Fita 1[{registro['cabeca_anterior']}]")

    # Limpa o histórico após o Retrace
    historico.clear()

    # =========================================================================
    # RESULTADO FINAL APÓS OS 3 ESTÁGIOS
    # =========================================================================
    print("\n" + "=" * 70)
    print("RESULTADO FINAL DA SIMULACAO REVERSIVEL")
    print("=" * 70)
    print(f"Estado final: q{estado}")
    print(f"Fita 1 (Input Reconstruido): {texto_da_fita(fita)}")
    print(f"Fita 2 (History Limpo):       {texto_da_fita({})}")
    print(f"Fita 3 (Output Copiado):     {texto_da_fita(fita_output)}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())