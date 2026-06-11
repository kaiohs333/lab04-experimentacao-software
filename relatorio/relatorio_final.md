# Visualização de Dados: Programa Bolsa Família

**Lab04 — Experimentação de Software**

## Autores

- Kaio Henrique Oliveira da Silveira Barbosa
- Lucas Carvalho

---

## Índice

1. [Introdução](#1-introdução)
2. [Questões de Pesquisa](#2-questões-de-pesquisa)
3. [Metodologia](#3-metodologia)
   - 3.1 [Materiais e Ferramentas](#31-materiais-e-ferramentas)
   - 3.2 [Fonte e Coleta dos Dados](#32-fonte-e-coleta-dos-dados)
   - 3.3 [Definição das Métricas](#33-definição-das-métricas)
   - 3.4 [Fluxo de Execução](#34-fluxo-de-execução)
   - 3.5 [Caracterização do Dataset](#35-caracterização-do-dataset)
4. [Resultados](#4-resultados)
   - 4.1 [RQ01 — Distribuição por Estado](#41-rq01--distribuição-por-estado)
   - 4.2 [RQ02 — Evolução Temporal](#42-rq02--evolução-temporal)
   - 4.3 [RQ03 — Valor Médio por Região](#43-rq03--valor-médio-por-região)
   - 4.4 [RQ04 — Municípios com Mais Beneficiários](#44-rq04--municípios-com-mais-beneficiários)
5. [Discussão dos Resultados](#5-discussão-dos-resultados)
6. [Conclusão](#6-conclusão)

---

## 1. Introdução

O Programa Bolsa Família é uma das maiores políticas de transferência de renda do mundo. Criado em 2003, o programa beneficia famílias em situação de vulnerabilidade social no Brasil, fornecendo suporte financeiro mensal condicionado ao cumprimento de requisitos nas áreas de saúde e educação. Ao longo de sua trajetória, o programa passou por reformulações significativas: foi temporariamente substituído pelo *Auxílio Brasil* entre agosto de 2021 e fevereiro de 2023, sendo relançado como *Novo Bolsa Família* em março de 2023, com critérios e valores atualizados.

Compreender como o programa se distribui geograficamente, como evoluiu ao longo do tempo e quais municípios concentram maior número de beneficiários é fundamental para avaliar seu alcance e efetividade como política pública. Este trabalho explora os dados públicos do Bolsa Família disponibilizados pelo Portal da Transparência do Governo Federal, utilizando técnicas de Business Intelligence para responder a quatro questões de pesquisa definidas a seguir.

A análise baseia-se em um snapshot de **3.494 municípios** com beneficiários ativos em dezembro de 2023, totalizando **16,3 milhões de beneficiários** e **R$ 10,7 bilhões** pagos no mês de referência. Para a análise temporal, foram coletados dados das 27 capitais estaduais ao longo de todos os meses de 2023 e de dezembro de 2019 a 2022.

---

## 2. Questões de Pesquisa

| # | Questão de Pesquisa | Métrica analisada | Hipótese informal |
|---|---|---|---|
| **RQ01** | Como se distribui o número de beneficiários do Bolsa Família entre os estados brasileiros? | Total de beneficiários e valor pago por estado (Dez/2023) | Estados do Nordeste e Norte concentram a maior proporção de beneficiários, por apresentarem índices mais elevados de pobreza. |
| **RQ02** | Como evoluiu o valor total pago pelo programa ao longo dos anos (2019–2023)? | Total pago e valor médio por beneficiário, por período | O valor médio por beneficiário cresceu progressivamente, com saltos expressivos em 2022 (Auxílio Brasil) e 2023 (Novo Bolsa Família). |
| **RQ03** | Qual é o valor médio recebido por beneficiário em cada região do Brasil? | Valor médio = total pago / total de beneficiários, por região (Dez/2023) | Regiões Norte e Nordeste apresentam maior valor médio por beneficiário, em razão do perfil socioeconômico das famílias atendidas. |
| **RQ04** | Quais municípios concentram o maior número de beneficiários? | Ranking de municípios por total de beneficiários (Dez/2023) | Grandes centros urbanos, especialmente no Nordeste e Sudeste, lideram o ranking pelo volume absoluto de famílias atendidas. |

---

## 3. Metodologia

### 3.1 Materiais e Ferramentas

| Ferramenta / Recurso | Finalidade |
|---|---|
| Python 3.x | Scripts de coleta e processamento de dados |
| API Portal da Transparência | Fonte dos dados do Bolsa Família por município |
| API IBGE Localidades | Obtenção de todos os códigos IBGE municipais |
| pandas | Manipulação, agregação e exportação dos dados |
| python-dotenv | Gerenciamento da chave de acesso à API |
| Power BI | Construção do dashboard de visualização |

### 3.2 Fonte e Coleta dos Dados

Os dados foram obtidos por meio da **API pública do Portal da Transparência** (https://api.portaldatransparencia.gov.br), que oferece acesso gratuito mediante cadastro de chave de API. O programa passou por três denominações no período analisado, cada uma com um endpoint próprio:

| Período | Nome do Programa | Endpoint da API |
|---|---|---|
| Até dez/2020 | Bolsa Família | `/bolsa-familia-por-municipio` |
| Jan/2021 – Fev/2023 | Auxílio Brasil | `/auxilio-brasil-por-municipio` |
| Mar/2023 em diante | Novo Bolsa Família | `/novo-bolsa-familia-por-municipio` |

A coleta foi estruturada em duas estratégias complementares:

- **Snapshot (Dez/2023):** coleta para todos os 5.571 municípios brasileiros via requisições paralelas (8 workers), obtendo dados de 3.494 municípios com beneficiários ativos. Os 2.077 municípios sem dados correspondem, majoritariamente, a pequenos municípios das regiões Sul e Centro-Oeste, onde o índice de beneficiários é menor.

- **Série histórica (capitais estaduais):** coleta sequencial para as 27 capitais estaduais, cobrindo todos os meses de 2023 e os meses de dezembro de 2019 a 2022. Essa amostra permite analisar tendências temporais de forma representativa.

### 3.3 Definição das Métricas

| Métrica | Descrição |
|---|---|
| `qtd_beneficiarios` | Número de famílias beneficiadas no município no período |
| `valor` | Valor total pago às famílias no município no período (R$) |
| `valor_medio_por_beneficiario` | Valor total / quantidade de beneficiários |
| `regiao` | Região geográfica (Norte, Nordeste, Centro-Oeste, Sudeste, Sul) |

> **Medida de tendência central adotada:** média simples (`valor / qtd_beneficiarios`), adequada para dados de pagamentos uniformes dentro de cada município. A mediana foi considerada, porém os dados já são agregados por município — não há distribuição de valores individuais disponível na API.

### 3.4 Fluxo de Execução

O processo de coleta e processamento foi estruturado em duas etapas sequenciais:

**Etapa 1 — `collect_data.py`**
Obtém os códigos IBGE de todos os municípios via API do IBGE, consulta a API do Portal da Transparência com o endpoint correto para cada período e salva os resultados em arquivos JSON em `data/raw/`.

**Etapa 2 — `process_data.py`**
Carrega os JSONs brutos, normaliza os campos, mapeia estados às regiões geográficas e gera os CSVs agregados em `data/processed/`, prontos para importação no BI.

### 3.5 Caracterização do Dataset

A tabela abaixo resume as principais características do dataset utilizado na análise de dezembro de 2023 (snapshot completo):

| Característica | Valor |
|---|---|
| Municípios com beneficiários | 3.494 |
| Total de beneficiários | 16.341.242 |
| Total pago | R$ 10.741.381.705,00 |
| Valor médio nacional por beneficiário | R$ 657,34 |
| Estados com dados | 20 |
| Regiões representadas | Norte, Nordeste, Sudeste |

| Região | Municípios | Beneficiários | Total pago | Valor médio |
|---|---:|---:|---:|---:|
| Nordeste | 1.726 | 9.393.481 | R$ 6.134.782.864 | R$ 653,09 |
| Sudeste | 1.247 | 4.378.327 | R$ 2.844.751.667 | R$ 649,73 |
| Norte | 448 | 2.569.434 | R$ 1.761.847.174 | R$ 685,69 |

> **Nota sobre cobertura:** As regiões Sul e Centro-Oeste não aparecem no snapshot de Dez/2023 pois a maioria de seus municípios retornou dados vazios via API — o que reflete a menor incidência do programa nessas regiões mais desenvolvidas. Dados das capitais dessas regiões estão disponíveis na série histórica.

*[Inserir visualização de caracterização do dataset — Sprint 1]*

---

## 4. Resultados

### 4.1 RQ01 — Distribuição por Estado

**Pergunta:** Como se distribui o número de beneficiários do Bolsa Família entre os estados brasileiros?

Os dez estados com maior número de beneficiários em dezembro de 2023 são apresentados abaixo:

| UF | Estado | Região | Beneficiários | Total pago | Valor médio |
|---|---|---|---:|---:|---:|
| BA | Bahia | Nordeste | 2.447.388 | R$ 1.584.872.938 | R$ 647,58 |
| RJ | Rio de Janeiro | Sudeste | 1.724.036 | R$ 1.114.805.798 | R$ 646,63 |
| PE | Pernambuco | Nordeste | 1.611.495 | R$ 1.045.945.466 | R$ 649,05 |
| MG | Minas Gerais | Sudeste | 1.603.358 | R$ 1.039.676.121 | R$ 648,44 |
| CE | Ceará | Nordeste | 1.465.651 | R$ 958.284.427 | R$ 653,83 |
| PA | Pará | Norte | 1.316.952 | R$ 883.787.104 | R$ 671,09 |
| MA | Maranhão | Nordeste | 1.175.073 | R$ 794.523.127 | R$ 676,15 |
| SP | São Paulo | Sudeste | 745.676 | R$ 489.588.271 | R$ 656,57 |
| PB | Paraíba | Nordeste | 674.395 | R$ 436.526.978 | R$ 647,29 |
| AM | Amazonas | Norte | 648.075 | R$ 459.446.491 | R$ 708,94 |

A hipótese de que os estados do Nordeste concentrariam o maior número de beneficiários é **confirmada**: os estados nordestinos dominam o ranking, com destaque para Bahia (2,4 milhões), Pernambuco (1,6 milhões) e Ceará (1,5 milhões). Roraima apresenta o maior valor médio por beneficiário (R$ 734,75), indicando que as famílias atendidas nesse estado possuem maior grau de vulnerabilidade socioeconômica.

*[Inserir gráfico de barras: beneficiários por estado — Sprint 2]*

*[Inserir mapa coroplético do Brasil — Sprint 2]*

---

### 4.2 RQ02 — Evolução Temporal

**Pergunta:** Como evoluiu o valor total pago pelo programa ao longo dos anos (2019–2023)?

A tabela abaixo apresenta a evolução do programa nas 27 capitais estaduais, considerando o mês de dezembro de cada ano:

| Ano | Programa | Total de beneficiários (capitais) | Total pago (capitais) | Valor médio por beneficiário |
|---|---|---:|---:|---:|
| 2019 | Bolsa Família | 1.995.790 | R$ 337.985.504 | R$ 169,35 |
| 2020 | Bolsa Família | 2.322.043 | R$ 395.314.012 | R$ 170,24 |
| 2021 | Auxílio Brasil | 2.282.468 | R$ 474.283.691 | R$ 207,79 |
| 2022 | Auxílio Brasil | 3.303.527 | R$ 1.481.149.474 | R$ 448,35 |
| 2023 | Novo Bolsa Família | 3.981.615 | R$ 2.590.891.647 | R$ 650,71 |

A hipótese de crescimento progressivo do valor médio é **confirmada**. Dois saltos se destacam:

- **2021→2022:** o valor médio quase dobrou (R$ 207 → R$ 448), reflexo da expansão do Auxílio Brasil com benefícios adicionais introduzidos no segundo semestre de 2022.
- **2022→2023:** novo aumento expressivo (R$ 448 → R$ 651) com o relançamento do Novo Bolsa Família, que elevou o benefício mínimo e ampliou a cobertura.

O número de beneficiários nas capitais também cresceu 99% entre 2019 e 2023 (1,99 milhão → 3,98 milhões), indicando expansão significativa do programa.

*[Inserir gráfico de linha: evolução anual do valor médio — Sprint 2]*

*[Inserir gráfico de linha: evolução mensal em 2023 — Sprint 2]*

---

### 4.3 RQ03 — Valor Médio por Região

**Pergunta:** Qual é o valor médio recebido por beneficiário em cada região do Brasil?

| Região | Municípios | Beneficiários | Total pago | Valor médio por beneficiário |
|---|---:|---:|---:|---:|
| Norte | 448 | 2.569.434 | R$ 1.761.847.174 | **R$ 685,69** |
| Nordeste | 1.726 | 9.393.481 | R$ 6.134.782.864 | R$ 653,09 |
| Sudeste | 1.247 | 4.378.327 | R$ 2.844.751.667 | R$ 649,73 |

A hipótese de que a região Norte apresentaria maior valor médio por beneficiário é **confirmada** (R$ 685,69 vs R$ 653,09 no Nordeste). Esse resultado pode refletir o perfil de maior vulnerabilidade das famílias atendidas na região amazônica, bem como o custo de vida mais elevado em municípios de difícil acesso. A diferença entre Nordeste e Sudeste é pequena (R$ 3,36), sugerindo uniformidade no critério de benefício.

*[Inserir gráfico de barras: valor médio por região — Sprint 2]*

---

### 4.4 RQ04 — Municípios com Mais Beneficiários

**Pergunta:** Quais municípios concentram o maior número de beneficiários?

Os dez municípios com maior número de beneficiários em dezembro de 2023:

| # | Município | UF | Região | Beneficiários | Total pago | Valor médio |
|---|---|---|---|---:|---:|---:|
| 1 | Rio de Janeiro | RJ | Sudeste | 575.085 | R$ 369.688.762 | R$ 642,84 |
| 2 | Fortaleza | CE | Nordeste | 343.346 | R$ 221.155.689 | R$ 644,12 |
| 3 | Salvador | BA | Nordeste | 298.759 | R$ 187.523.199 | R$ 627,67 |
| 4 | Manaus | AM | Norte | 274.652 | R$ 188.077.509 | R$ 684,78 |
| 5 | Belém | PA | Norte | 190.133 | R$ 119.585.743 | R$ 628,96 |
| 6 | Recife | PE | Nordeste | 147.155 | R$ 93.533.147 | R$ 635,61 |
| 7 | Belo Horizonte | MG | Sudeste | 134.286 | R$ 85.749.693 | R$ 638,56 |
| 8 | Nova Iguaçu | RJ | Sudeste | 125.142 | R$ 83.194.445 | R$ 664,80 |
| 9 | Duque de Caxias | RJ | Sudeste | 123.099 | R$ 80.033.713 | R$ 650,16 |
| 10 | São Luís | MA | Nordeste | 121.532 | R$ 80.704.262 | R$ 664,06 |

A hipótese é **parcialmente confirmada**: grandes centros urbanos lideram o ranking em volume absoluto, com destaque para Rio de Janeiro (575 mil beneficiários). No entanto, a presença de Manaus (4º) e Belém (5º) evidencia o peso da região Norte no programa, mesmo em volume absoluto. Chama atenção que Nova Iguaçu e Duque de Caxias — municípios da Baixada Fluminense, não capitais — figuram no top 10, superando metrópoles como São Paulo (não listado entre os dez primeiros), o que aponta para alta concentração de vulnerabilidade social na região metropolitana do Rio de Janeiro.

*[Inserir gráfico de barras horizontal: top 20 municípios — Sprint 2]*

---

## 5. Discussão dos Resultados

### 5.1 Concentração Regional

Os dados confirmam que o Nordeste é a região com maior concentração de beneficiários em termos absolutos: aproximadamente **57,5% dos beneficiários** pertencem a municípios nordestinos. Isso reflete o histórico de desigualdade regional no Brasil, onde estados como Bahia, Ceará e Maranhão apresentam os maiores índices de pobreza extrema.

A região Norte, embora menos populosa, apresenta o **maior valor médio por beneficiário** (R$ 685,69), o que sugere que as famílias atendidas nessa região enfrentam condições de vulnerabilidade mais severas ou têm acesso a benefícios complementares do programa.

### 5.2 Evolução do Programa

O crescimento do valor médio de R$ 169 (2019) para R$ 651 (2023) representa um aumento de **285%** em quatro anos. Esse crescimento reflete três fases distintas:

1. **Bolsa Família original (2019–2020):** valor médio estagnado em torno de R$ 170, sem reajustes significativos.
2. **Auxílio Brasil (2021–2022):** aumento gradual, com grande salto em 2022 devido a benefícios extras criados próximos às eleições presidenciais.
3. **Novo Bolsa Família (2023):** consolidação do benefício mínimo de R$ 600 e benefício adicional por criança de até 6 anos, elevando a média a R$ 651.

### 5.3 Anomalia na Baixada Fluminense

A presença de Nova Iguaçu e Duque de Caxias no top 10 de beneficiários — superando São Paulo (maior cidade do país) — indica uma concentração incomum de vulnerabilidade social na Região Metropolitana do Rio de Janeiro. Esse padrão merece investigação adicional, pois pode refletir tanto a alta densidade populacional da Baixada quanto a efetividade do cadastramento nessa região.

### 5.4 Limitações do Estudo

- **Cobertura regional incompleta:** municípios das regiões Sul e Centro-Oeste com poucos ou nenhum beneficiário não retornaram dados via API no snapshot de Dez/2023, limitando a análise dessas regiões a dados das capitais.
- **Série histórica restrita a capitais:** para a análise temporal (RQ02), foram utilizadas apenas as 27 capitais estaduais como proxy do comportamento nacional. Embora representativas, as capitais tendem a concentrar proporção maior de beneficiários do que municípios menores.
- **Dados agregados por município:** a API não fornece distribuição de valores individuais, impossibilitando análises de dispersão intra-municipal.

---

## 6. Conclusão

Os dados do Programa Bolsa Família revelam um cenário de **acentuada concentração regional** e **crescimento expressivo do valor do benefício** ao longo do período analisado. As quatro questões de pesquisa foram respondidas com base nos dados coletados:

| RQ | Hipótese | Resultado | Confirmada? |
|---|---|---|:---:|
| RQ01 | Nordeste concentra mais beneficiários | BA, PE, CE e MA lideram o ranking nacional | **Sim** |
| RQ02 | Valor médio cresceu progressivamente, com saltos em 2022 e 2023 | +285% entre 2019 e 2023; dois saltos expressivos identificados | **Sim** |
| RQ03 | Norte e Nordeste têm maior valor médio | Norte lidera (R$ 685,69 vs R$ 653,09 no Nordeste) | **Parcialmente** |
| RQ04 | Grandes centros urbanos lideram em volume absoluto | Rio de Janeiro, Fortaleza e Salvador lideram; Baixada Fluminense destoa | **Parcialmente** |

Os achados reforçam a relevância do programa como principal mecanismo de redistribuição de renda no Brasil e evidenciam a persistente desigualdade regional. A expansão observada entre 2019 e 2023 — tanto em número de beneficiários quanto em valor do benefício — indica uma mudança de escopo do programa, que passou de uma política de complementação de renda para uma política mais ampla de garantia de renda mínima.

---

## Referências

- Portal da Transparência do Governo Federal: https://portaldatransparencia.gov.br
- API de Dados Abertos: https://api.portaldatransparencia.gov.br/api-de-dados
- IBGE API de Localidades: https://servicodados.ibge.gov.br/api/v1/localidades/municipios
- Ministério do Desenvolvimento Social — Bolsa Família: https://www.gov.br/cidadania/pt-br/acoes-e-programas/bolsa-familia
