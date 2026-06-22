# Zapsign Monitor de Contratos

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-Data%20Analysis-150458?logo=pandas&logoColor=white)
![Zapsign API](https://img.shields.io/badge/Zapsign%20API-v1-green?logo=swagger&logoColor=white)

## 📋 Descrição do Projeto

O **Zapsign Monitor de Contratos** é uma solução de automação em Python que simplifica o acompanhamento de contratos pendentes na plataforma [Zapsign](https://www.zapsign.com.br/). Ele se conecta diretamente à API oficial da Zapsign, recupera documentos pendentes localizados no folder `/Contratos`, extrai os signatários de cada contrato e gera relatórios individuais em Excel para os principais responsáveis, além de um consolidado com os demais signatários pendentes.

Ideal para equipes jurídicas, comerciais e administrativas que precisam monitorar diariamente o status de assinatura de contratos de forma automatizada e organizada.

## ✨ Funcionalidades principais

- 🔗 Integração com a API oficial da Zapsign (`/api/v1/docs/`).
- 📁 Filtro automático de documentos por status `pending`, folder `/Contratos` e não deletados.
- ⚙️ Paginação completa para buscar todos os documentos, independentemente da quantidade.
- 👥 Extração e explosão dos signatários (`signers`) em linhas individuais.
- 🎯 Filtragem de signatários pendentes (`nao_abriu` ou `abriu`).
- 📊 Geração de arquivos Excel personalizados para cada signatário principal.
- 📈 Relatório consolidado com todos os signatários pendentes restantes.
- 💾 Exportação dos dados completos e filtrados para análises posteriores.

## 🔄 Como funciona o fluxo

O projeto é composto por duas funções principais que trabalham em conjunto:

### 1. `get_docs()`

Responsável pela integração com a Zapsign API:

1. Lê o token de API configurado no arquivo `.env`.
2. Envia requisições GET para o endpoint `https://api.zapsign.com.br/api/v1/docs/`.
3. Aplica os filtros:
   - `include_signers=true`
   - `status=pending`
   - `deleted=false`
   - `folder_path=/Contratos`
4. Percorre todas as páginas de resultados até não haver mais documentos retornados.
5. Retorna uma lista completa com todos os documentos encontrados.

### 2. `analizer(dados)`

Responsável pelo processamento e geração dos relatórios:

1. Converte a lista de documentos em um `DataFrame` do pandas.
2. Converte a coluna `signers` — armazenada como string representando uma lista de dicionários — para objetos Python reais usando `ast.literal_eval`.
3. Aplica `explode()` na coluna `signers`, transformando cada signatário em uma linha independente.
4. Filtra apenas signatários pendentes, cujo status seja `nao_abriu` ou `abriu`.
5. Gera arquivos Excel individuais para os signatários principais:
   - `lucas_pendentes.xlsx`
   - `david_pendentes.xlsx`
   - `gabi_pendentes.xlsx`
   - `ju_pendentes.xlsx`
6. Gera o arquivo `outros_sig_pendentes.xlsx` com todos os demais signatários pendentes.
7. Salva os dados completos dos signatários em `signers.xlsx`.
8. Salva os dados filtrados de pendentes em `relat.xlsx`.

## 🛠️ Tecnologias utilizadas

- **Python 3** — linguagem principal da automação.
- **pandas** — manipulação de dados, filtragem e exportação para Excel.
- **requests** — realização das chamadas HTTP à API da Zapsign.
- **python-dotenv** — carregamento seguro de variáveis de ambiente.
- **ast.literal_eval** — conversão segura de strings para estruturas Python.

## ⚙️ Instalação e configuração

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/zapsign_scraping.git
cd zapsign-monitor-contratos
```
