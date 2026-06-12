# Visualização de Dados: Programa Bolsa Família

**Lab04 — Experimentação de Software**

## Autores

- Kaio Henrique Oliveira da Silveira Barbosa
- Lucas Carvalho

---

## Descrição

Este projeto realiza a coleta, processamento e visualização de dados públicos do **Programa Bolsa Família** disponibilizados pelo Portal da Transparência do Governo Federal. O objetivo é explorar a distribuição geográfica, a evolução temporal e as características dos beneficiários do programa, utilizando uma ferramenta de Business Intelligence para responder às questões de pesquisa propostas.

Os dados abrangem **3.494 municípios** com beneficiários em dezembro de 2023, totalizando **16,3 milhões de beneficiários** e **R$ 107 bilhões** pagos no período analisado (2019–2023). Para a análise temporal, foram coletados dados das 27 capitais estaduais entre 2019 e 2023.

---

## Questões de Pesquisa

| # | Questão | Dados utilizados |
|---|---|---|
| **RQ01** | Como se distribui o número de beneficiários do Bolsa Família entre os estados brasileiros? | Snapshot Dez/2023 — todos os municípios |
| **RQ02** | Como evoluiu o valor total pago pelo programa ao longo dos anos (2019–2023)? | Capitais estaduais — Dez de cada ano + mensal 2023 |
| **RQ03** | Qual é o valor médio recebido por beneficiário em cada região do Brasil? | Snapshot Dez/2023 — todos os municípios |
| **RQ04** | Quais municípios concentram o maior número de beneficiários? | Snapshot Dez/2023 — top 50 municípios |

---

## Dashboard

### Caracterização do Dataset

![Caracterização do Dataset](https://github.com/kaiohs333/lab04-experimentacao-software/blob/main/imagens/Cateriza%C3%A7%C3%A3o%20do%20dataset.png?raw=true)

> Visão geral do dataset: distribuição geográfica dos beneficiários por estado e região, com indicadores de total de beneficiários (16 Mi), valor pago (R$ 10,7 Bi), estados cobertos (20) e municípios atendidos (3 Mil).

---

### RQ1 — Como se distribui o número de beneficiários entre os estados?

![RQ1](https://github.com/kaiohs333/lab04-experimentacao-software/blob/main/imagens/RQ1.png?raw=true)

> A Bahia lidera com 2,4 milhões de beneficiários, seguida por Rio de Janeiro (1,7 Mi) e Pernambuco (1,6 Mi). Os estados do Nordeste concentram a maior parte dos beneficiários, refletindo as desigualdades regionais do país. O valor médio por beneficiário varia entre R$636 (Rio Grande do Norte) e R$734 (Roraima).

---

### RQ2 — Como evoluiu o número de beneficiários e os valores pagos entre 2019 e 2023?

![RQ2](https://github.com/kaiohs333/lab04-experimentacao-software/blob/main/imagens/RQ2.png?raw=true)

> O programa apresentou crescimento expressivo no período, com o número de beneficiários saltando de 2 milhões (2019) para quase 4 milhões (2023) nas capitais analisadas. O valor médio por beneficiário também cresceu significativamente, especialmente a partir de 2022 com a transição para o Auxílio Brasil e posteriormente o Novo Bolsa Família. Em 2023, os meses de janeiro e fevereiro registraram menor volume de beneficiários, com crescimento ao longo do ano.

---

### RQ3 — Existe diferença no valor médio pago por beneficiário entre as regiões?

![RQ3](https://github.com/kaiohs333/lab04-experimentacao-software/blob/main/imagens/RQ3.png?raw=true)

> Existe diferença entre as regiões: a região Norte apresenta o maior valor médio por beneficiário (R$686), seguida pelo Nordeste (R$653) e Sudeste (R$650). Essa diferença pode estar relacionada ao perfil socioeconômico das famílias atendidas em cada região, com famílias do Norte apresentando maior vulnerabilidade e, portanto, recebendo benefícios mais altos.

---

### RQ4 — Quais municípios concentram o maior número de beneficiários?

![RQ4](https://github.com/kaiohs333/lab04-experimentacao-software/blob/main/imagens/RQ4.png?raw=true)

> O Rio de Janeiro lidera com 575 mil beneficiários, seguido por Fortaleza (343 mil) e Salvador (299 mil). O gráfico de dispersão revela que municípios do Norte, apesar de menor volume de beneficiários, tendem a apresentar valor médio mais alto — como Manaus (R$685) e Belém. Os municípios do Sudeste concentram grande volume mas com valor médio menor, indicando um perfil diferente de beneficiários.

---

## Estrutura do Repositório

```
.
├── data/
│   ├── raw/
│   │   ├── snapshot_202312_all.json       # Todos os municípios — Dez/2023
│   │   └── capitais_AAAAMM.json           # 27 capitais — múltiplos períodos
│   └── processed/
│       ├── caracterizacao_dataset.csv     # Visão geral do dataset por estado
│       ├── rq1_beneficiarios_por_estado.csv
│       ├── rq2_evolucao_anual_capitais.csv
│       ├── rq2_evolucao_mensal_2023.csv
│       ├── rq3_media_por_regiao.csv
│       └── rq4_top_municipios.csv
├── imagens/
│   ├── Caterização do dataset.png
│   ├── RQ1.png
│   ├── RQ2.png
│   ├── RQ3.png
│   └── RQ4.png
├── scripts/
│   ├── collect_data.py                    # Coleta via API do Portal da Transparência
│   └── process_data.py                    # Processamento e geração dos CSVs
├── relatorio/
│   └── relatorio_final.md                 # Relatório final
├── .env.example                           # Modelo do arquivo de configuração
├── requirements.txt                       # Dependências Python
└── .gitignore
```

---

## Como Executar

### 1. Criar ambiente virtual e instalar dependências

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar chave de API

Cadastre seu e-mail em https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email e crie o arquivo `.env` na raiz:

```
API_KEY=sua_chave_aqui
```

### 3. Coleta de dados

```bash
python scripts/collect_data.py
```

Coleta realizada em duas etapas:
- **Snapshot (Dez/2023):** todos os ~5.570 municípios via requisições paralelas (~15 min)
- **Histórico:** 27 capitais estaduais para todos os meses de 2023 e Dezembro de 2019–2022 (~6 min)

### 4. Processamento e geração dos CSVs

```bash
python scripts/process_data.py
```

Os CSVs prontos para importação no BI serão salvos em `data/processed/`.

---

## Dataset

| Característica | Valor |
|---|---|
| Fonte | Portal da Transparência — API pública |
| Endpoint principal | `/novo-bolsa-familia-por-municipio` |
| Período do snapshot | Dezembro de 2023 |
| Municípios com dados | 3.494 |
| Total de beneficiários (Dez/2023) | 16.341.242 |
| Total pago (Dez/2023) | R$ 10.741.381.705,00 |
| Período histórico (capitais) | Dez/2019 a Dez/2023 + mensal 2023 |

> **Nota:** Os programas passaram por três nomes no período analisado: *Bolsa Família* (até 2020), *Auxílio Brasil* (2021–fev/2023) e *Novo Bolsa Família* (mar/2023 em diante). Cada período utiliza o endpoint correto da API.

---

## Dependências

- Python 3.x
- requests
- pandas
- python-dotenv
