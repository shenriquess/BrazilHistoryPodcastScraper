# Web Scraper de Podcasts de História do Brasil

Este script Python foi desenvolvido para fazer web scraping dos podcasts do site "Leitura ObrigaHistória", focando especificamente em conteúdo relacionado à História do Brasil. O scraper descobre automaticamente os episódios dos podcasts, filtra o conteúdo relacionado à história brasileira e salva os resultados em formato CSV.

## Funcionalidades

- Descoberta automática de podcasts a partir do site principal
- Filtragem de conteúdo baseada em palavras-chave relacionadas ao Brasil
- Tratamento de paginação para coleta completa de dados
- Suporte a codificação UTF-8 para tratamento adequado de caracteres em português
- Tratamento robusto de erros e logging
- Exportação em CSV com informações dos episódios
- Geração de estatísticas básicas

## Requisitos

### Versão do Python
- Python 3.6 ou superior

### Bibliotecas Necessárias
Instale as dependências usando o pip:
```bash
pip install -r requirements.txt
```

Conteúdo do arquivo `requirements.txt`:
```
requests>=2.25.1
beautifulsoup4>=4.9.3
pandas>=1.2.0
```

## Instalação

1. Clone este repositório:
```bash
git clone [url-do-repositorio]
cd [nome-do-diretorio]
```

2. Crie e ative um ambiente virtual (recomendado):
```bash
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Como Usar

1. Execute o script principal:
```bash
python scraper.py
```

O script irá:
- Acessar o site do Leitura ObrigaHistória
- Descobrir automaticamente todos os podcasts disponíveis
- Fazer scraping de cada podcast em busca de episódios sobre História do Brasil
- Salvar os resultados em arquivos CSV separados na pasta `podcasts_brasil`

## Estrutura do Projeto

```
.
├── scraper.py           # Script principal
├── requirements.txt     # Dependências do projeto
├── README.md           # Este arquivo
└── podcasts_brasil/    # Pasta onde os resultados são salvos
```

## Detalhes Técnicos

### Palavras-chave para Filtragem
O script identifica conteúdo relacionado à História do Brasil usando uma lista de palavras-chave que inclui termos como:
- brasil, brasileiro, brasileira
- império, dom pedro
- república, colonial, colônia
- independência, ditadura
- E outros termos históricos relevantes

### Formato dos Dados Coletados
Os arquivos CSV gerados contêm as seguintes informações para cada episódio:
- Título do episódio
- Link do episódio
- Data de publicação

### Tratamento de Caracteres Especiais
O script foi desenvolvido com atenção especial ao tratamento de caracteres especiais em português:
- Utiliza codificação UTF-8 em todas as operações
- Garante a preservação de acentos e caracteres especiais nos arquivos CSV
- Verifica a integridade dos dados após o salvamento

## Tratamento de Erros

O script inclui tratamento robusto de erros para:
- Falhas de conexão com o site
- Problemas de parsing do HTML
- Erros de codificação de caracteres
- Falhas no salvamento dos arquivos

Em caso de erro ao salvar o arquivo principal, um arquivo de backup é automaticamente gerado.

## Limitações e Considerações

- O script respeita um intervalo de 1 segundo entre requisições para não sobrecarregar o servidor
- A detecção de conteúdo sobre História do Brasil é baseada em palavras-chave e pode ocasionalmente incluir ou excluir conteúdo incorretamente
- A estrutura do site pode mudar, necessitando atualizações no código

## Suporte

Em caso de problemas ou dúvidas:
1. Verifique se todas as dependências estão instaladas corretamente
2. Confirme se está usando a versão correta do Python
3. Verifique se há erros no console
