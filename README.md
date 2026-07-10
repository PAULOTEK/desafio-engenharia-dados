# Projeto Bronze / Silver / Gold para SiCooperative Asset Management

## Visão geral

Este projeto demonstra uma arquitetura moderna de dados para Asset Management usando:

- **PostgreSQL** como fonte transacional
- **Control-M** para orquestração
- **Avro** como formato de aterrissagem na **bronze layer**
- **Spark / PySpark** para processamento distribuído
- **Delta Lake** para as camadas **silver** e **gold**
- **Docker Compose** para ambiente local reproduzível
- **pytest** para testes unitários

O objetivo é consolidar posições de fundos e tabelas relacionadas em uma estrutura analítica confiável, com trilha clara de dados brutos até dados curados.

---

## Arquitetura proposta

### Camadas

**Bronze**
- Dados extraídos do PostgreSQL
- Persistidos em **Avro**
- Mantidos sem tratamento de negócio, apenas padronização técnica mínima

**Silver**
- Leitura dos arquivos Avro da bronze
- Limpeza, padronização, enriquecimento e regras de negócio
- Persistência em **Delta Lake**

**Gold**
- Visões analíticas prontas para consumo
- Agregações e indicadores por fundo, ativo, emissor, indexador e data
- Persistência em **Delta Lake**

### Fluxo

1. **Control-M** dispara o job de extração
2. Spark lê dados do PostgreSQL
3. Dados são gravados em Avro na bronze
4. Spark lê a bronze, trata e grava silver em Delta
5. Spark gera gold a partir da silver em Delta
6. Relatórios e ferramentas consomem a gold

---

## Estrutura do repositório

```text
desafio-engenharia-dados/
├── README.md
├── docker-compose.yml
├── requirements.txt
├── scripts/
│   └── run_pipeline.sh
├── sql/
│   ├── 01_schema.sql
│   ├── 02_seed.sql
│   └── 03_views.sql
├── src/
│   ├── pipeline.py
│   ├── jobs/
│   │   ├── bronze_job.py
│   │   ├── silver_job.py
│   │   ├── gold_job.py
│   │   └── export_job.py
│   ├── transforms/
│   │   ├── bronze_extractor.py
│   │   ├── silver_transformer.py
│   │   ├── gold_builder.py
│   │   └── flat_file_writer.py
│   └── utils/
│       ├── logging_config.py
│       ├── paths.py
│       └── spark.py
└── tests/
    ├── test_silver_transformer.py
    ├── test_gold_builder.py
    ├── test_flat_file_writer.py
    └── test_paths.py
```
## Bronze layer

A bronze recebe os dados brutos extraídos do PostgreSQL e gravados em Avro.

### Objetivo da bronze
- Rastreabilidade
- Reprocessamento
- Preservação do dado original

---

## Silver layer

A silver executa as validações e padronizações.

### Regras típicas
- Normalização de nomes e tipos
- Remoção de duplicidades
- Tratamento de nulos críticos
- Enriquecimento com chaves e descrições
- Filtragem por registros válidos
- Cálculo de campos derivados

### transformações
- `financial_value = quantity * market_price`
- `nav_percentage` padronizado em decimal
- `operation_type` convertido para maiúsculo
- `position_date` em formato date

---

## Gold layer

A gold é orientada a consumo analítico.

### Exemplo de outputs
- Posição consolidada por fundo e data
- Exposição por emissor
- Exposição por classe de ativo
- Patrimônio por fundo
- Ranking de ativos por valor financeiro

### tabela gold

```text
fund_code | fund_name | position_date | asset_code | issuer_name | asset_type | quantity | market_price | financial_value | nav_percentage
```



---

## Control-M

## `control-m/job_flow.md`

```text
Job Flow:

1. JOB_EXTRACT_BRONZE
   - Type: Shell / Spark
   - Action: Extract PostgreSQL tables and save Avro in bronze layer

2. JOB_BUILD_SILVER
   - Type: Shell / Spark
   - Action: Read Avro bronze and write Delta silver

3. JOB_BUILD_GOLD
   - Type: Shell / Spark
   - Action: Read silver Delta and generate gold Delta

4. JOB_VALIDATION
   - Type: Shell
   - Action: Validate file existence, record counts and freshness
```

## `control-m/sample_job_definitions.md`

```text
Suggested Control-M parameters:

- JDBC_URL
- JDBC_USER
- JDBC_PASSWORD
- BRONZE_PATH
- SILVER_PATH
- GOLD_PATH
- LOG_PATH
- EXECUTION_DATE
```

---

## README.md completo

## Objetivo

Construir uma POC de dados para a SiCooperative Asset Management com foco em uma arquitetura em camadas:

- Bronze em Avro
- Silver em Delta Lake
- Gold em Delta Lake
- Orquestração via Control-M

## Por que essa arquitetura

- Bronze preserva o dado bruto
- Silver concentra padronização e regras de negócio
- Gold entrega consumo analítico rápido
- Delta Lake adiciona confiabilidade, ACID e evolução de schema
- Control-M encaixa bem em ambientes corporativos para agendamento e monitoramento

## Como rodar localmente

1. Subir os containers
```bash
docker compose up -d
```

2. Executar extração bronze
```bash
python -m src.jobs.bronze_job \
  --output ./data/bronze \
  --jdbc-url jdbc:postgresql://localhost:5432/asset_db \
  --user asset_user \
  --password asset_pass
```

3. Gerar silver
```bash
python -m src.jobs.silver_job \
  --bronze-path ./data/bronze \
  --silver-path ./data/silver
```

4. Gerar gold
```bash
python -m src.jobs.gold_job \
  --silver-path ./data/silver \
  --gold-path ./data/gold
```

5. Exportar o arquivo flat (CSV) consolidado em um diretório parametrizado
```bash
python -m src.jobs.export_job \
  --silver-path ./data/silver \
  --output-dir ./data/export \
  --filename consolidated_positions.csv
```

### Execução automatizada (pipeline completo)

Todas as etapas acima podem ser executadas de uma vez, com um único comando. Qualquer
falha em uma etapa aborta o processo e retorna código de saída diferente de zero:

```bash
python -m src.pipeline \
  --jdbc-url jdbc:postgresql://localhost:5432/asset_db \
  --user asset_user \
  --password asset_pass \
  --output-dir ./data/export
```

Ou, dentro do container Docker:

```bash
docker compose exec spark bash scripts/run_pipeline.sh
```

## Arquivo flat de saída (requisito principal)

O desafio pede um **único arquivo flat (CSV)** agregando as tabelas em uma visão única,
em um diretório parametrizado pelo usuário. Isso é atendido por `src/jobs/export_job.py`
(e pelo pipeline completo), que grava um único CSV com a seguinte estrutura:

```text
fund_code | fund_name | position_date | asset_code | asset_name | issuer_name | asset_type | quantity | market_price | financial_value | nav_percentage
```

Formatação de saída:
- Colunas numéricas (`quantity`, `market_price`, `financial_value`, `nav_percentage`) são gravadas com **2 casas decimais** (sem separador de milhar), para um CSV limpo.
- As linhas são ordenadas por `fund_code`, `asset_code`, `position_date`.
- Além do `.csv`, é gerado um `.txt` companheiro com a **tabela alinhada por coluna** (fixed-width) para leitura humana.

## Tratamento de erros e logging

- Logging estruturado via `src/utils/logging_config.py` (nível controlado por `LOG_LEVEL`), emitido em stderr.
- Cada job (`bronze`, `silver`, `gold`, `export`) valida entradas, registra o erro com contexto e **propaga** a falha com código de saída 1 — nada é silenciosamente ignorado.
- Falhas de leitura das camadas (bronze/silver) recebem mensagem indicando qual etapa anterior precisa ter rodado.
- Os recursos do Spark são liberados em `finally`, mesmo quando ocorre erro.
- Os transformadores validam colunas obrigatórias e lançam `ValueError` claro em vez de erros crípticos do Spark.

## Estrutura de saída

```text
/data/bronze
/data/silver
/data/gold
```

## Decisões de design

- PostgreSQL foi escolhido pela simplicidade e aderência ao desafio
- Avro foi usado na bronze por ser eficiente para aterrissagem e com schema embutido
- Delta Lake foi adotado em silver e gold para versionamento, confiabilidade e operação analítica
- PySpark foi escolhido para cumprir a exigência de processamento distribuído

## O que faria com mais tempo

- Incluir Airflow ou Control-M real com integração no ambiente
- Adicionar particionamento por data nas tabelas Delta
- Implementar data quality checks com Great Expectations
- Criar logging estruturado e métricas
- Adicionar testes de integração com Docker
- Implementar incremental load e CDC

## Dificuldades encontradas

- Tratar a granularidade entre posições, operações e preços
- Definir a melhor chave para seleção de preço vigente por data
- Harmonizar o fluxo bronze/silver/gold com persistência local

---

## Passos para criar a arquitetura em outra ferramenta

Se você quiser desenhar essa arquitetura em **draw.io**, **Lucidchart**, **Miro**, **Excalidraw** ou **Figma**, siga estes passos:

### 1. Criar três blocos principais
- **Bronze**
- **Silver**
- **Gold**

### 2. Inserir as fontes
À esquerda do fluxo, coloque:
- PostgreSQL
- Control-M

### 3. Definir o fluxo
Desenhe setas assim:

```text
PostgreSQL -> Bronze (Avro) -> Silver (Delta) -> Gold (Delta)
Control-M -> Bronze Job -> Silver Job -> Gold Job
```

### 4. Adicionar metadados
Inclua abaixo de cada camada:
- formato
- objetivo
- tipo de processamento

### 5. Destacar Control-M
Mostre o Control-M como a camada de orquestração, não de processamento.

### 6. Adicionar zonas de armazenamento
Se quiser ficar mais completo:
- Raw zone
- Curated zone
- Consumption zone

### 7. Finalizar com caixas de consumo
À direita do gold, adicione:
- Risk
- Compliance
- Gestão
- BI

---

## Sugestão de desenho textual da arquitetura

```text
[PostgreSQL]
     |
     v
[Control-M Orchestration]
     |
     v
[Bronze - Avro]
     |
     v
[Silver - Delta Lake]
     |
     v
[Gold - Delta Lake]
     |
     v
[Risk | Compliance | Gestão | BI]
```

---

## Próximos passos para deixar o projeto pronto para GitHub

1. Criar o repositório privado
2. Subir a estrutura de pastas
3. Colar os scripts SQL
4. Implementar os jobs PySpark
5. Adicionar os testes
6. Ajustar o Docker Compose
7. Escrever o README final
8. Versionar tudo com commits claros

---

## Recomendação final

Se a entrega for para entrevista, apresente o projeto com esta narrativa:

> A solução separa claramente ingestão, tratamento e consumo analítico. A bronze preserva os dados no formato Avro, a silver aplica regras e padronização em Delta Lake e a gold gera visões otimizadas para análise. A orquestração fica com o Control-M, enquanto o Spark garante o processamento distribuído.

---

Se quiser, no próximo passo eu posso transformar isso em um **repositório completo file-by-file**, te entregando cada arquivo separado com o conteúdo pronto para copiar e colar.