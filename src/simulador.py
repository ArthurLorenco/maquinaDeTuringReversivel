#!/usr/bin/env python3
"""Andamento 1: simula a MT original e registra o histórico dos passos."""

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


def main():
    try:
        quantidade_estados, transicoes, entrada = ler_descricao()
    except ValueError as erro:
        print(erro, file=sys.stderr)
        return 1

    fita = {posicao: simbolo for posicao, simbolo in enumerate(entrada)}
    historico = []
    estado = 1
    cabeca = 0
    passo = 0

    print("FASE 1 — simulacao da MT original")
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

        # Este registro contém exatamente o que será necessário para desfazer
        # o passo na fase de retrace implementada posteriormente.
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

    print("\nMT aceita.")
    print(f"Estado final: {estado}")
    print(f"Fita de trabalho: {texto_da_fita(fita)}")
    print(f"Passos registrados no historico: {len(historico)}")
    print("\nO retrace ainda sera implementado na proxima etapa.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
