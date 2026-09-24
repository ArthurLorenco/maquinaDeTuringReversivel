# Simulador de Máquina de Turing Reversível

## Descrição do trabalho

Implementação de um Simulador de [Máquina de Turing Reversível](http://www.math.ucsd.edu/~sbuss/CourseWeb/Math268_2013W/Bennett_Reversibiity.pdf "Máquina de Turing Reversível "). A seguir temos um exemplo de arquivo de entrada ilustrativo. A primeira linha apresenta números, que indicam: número de estados, número de símbolos no alfabeto de entrada, número de símbolos no alfabeto da fita e número de transições, respectivamente. A seguir, temos os estados, na próxima linha alfabeto de entrada e logo alfabeto da fita. Nas linhas sequentes temos a funcão de transição (como explicada no artigo). Depois da funcão de transição, segue uma entrada. Lembrando que o estado de aceitação é o último, no caso do exemplo, o 6.

LEMBRETE: o seu programa deve ler de um arquivo como ele lê da entrada padrão. Por exemplo, a chamada deve funcionar para:

```sh
./simulador < entrada-quintupla.txt
```

## Como executar

O repositório inclui um arquivo de entrada de exemplo na raiz. Não é necessário
instalar dependências além do Python 3.

```sh
./simulador < entrada-quintupla.txt
```

## Estrutura do repositório

```text
.
├── simulador                     # executável principal
├── entrada-quintupla.txt         # entrada de exemplo
├── src/
│   └── simulador.py              # implementação em Python
└── docs/
    └── Bennett_Reversibility.pdf # artigo de referência
```
