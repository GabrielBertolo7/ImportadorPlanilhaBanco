# Importador de Planilhas para Banco de Dados

Ferramenta com interface gráfica que lê uma planilha (`.xlsx`/`.xls`/`.csv`) e
grava os dados numa tabela MySQL/MariaDB, detectando automaticamente o tipo
correto de cada coluna (inteiro, decimal, data, data e hora ou texto), sem
nada fixo de cliente, banco ou tabela.

Este é o repositório de desenvolvimento. O guia de uso para quem só vai
**rodar** o programa está em [`GUIA_DE_USO.md`](GUIA_DE_USO.md).

## Arquitetura

```
importador/
  config.py    -> ConfiguracaoConexao + carregar/salvar (persistência local em conexao.json)
  planilha.py  -> leitura da planilha e normalização de nomes de coluna
  tipos.py     -> detecção de tipo por coluna (a parte "inteligente" da ferramenta)
  banco.py     -> conexão e DDL (criar/alterar tabela) no MySQL/MariaDB
  servico.py   -> orquestra planilha -> tipos -> banco (importar())
  gui.py       -> interface gráfica (Tkinter), só chama o servico

Importador.pyw   -> ponto de entrada (abre a janela)
empacotar.py     -> gera dist/ com o pacote pronto pra distribuir
tests/           -> testes unitários (pytest) das partes sem I/O
```

Cada módulo tem uma responsabilidade só: `tipos.py` e `planilha.py` não sabem
nada sobre banco de dados, `banco.py` não sabe nada sobre Tkinter, `gui.py` só
chama `servico.importar(...)` e mostra o progresso. Isso deixa a lógica de
detecção de tipo (a parte mais delicada) testável sem precisar de um banco de
dados rodando.

## Padrões

- **Strategy** para deteccão de tipo (`tipos.py`): cada regra de tipo (inteiro, decimal, data) é uma estratégia independente numa lista ordenada; adicionar um tipo novo é só acrescentar uma função na lista, sem tocar em `inferir_tipo_coluna`.
- **Repository** para acesso à tabela (`banco.py`): `TabelaRepository` concentra as operações que dependem de uma tabela específica (criar, alterar colunas, truncar, indexar), separado das operações de nível de servidor (criar banco, testar conexão).
- Textos de interface centralizados em `textos.py`, separados da lógica de montagem da tela em `gui.py`.

## Rodando os testes

```
pip install -r requisitos-dev.txt
pytest
```

Os testes cobrem `tipos.py` e `planilha.py` (funções puras, sem banco). A
integração real com o MySQL/MariaDB é validada manualmente rodando a própria
ferramenta.

## Empacotando para distribuir

```
python empacotar.py
```

Isso cria `dist/` com só o necessário para quem for usar o programa (sem
testes, sem cache, sem a `conexao.json` de teste do desenvolvedor). É o
conteúdo dessa pasta que deve ser copiado para onde for distribuir (rede
compartilhada, pendrive, etc.), não a raiz deste repositório.

Rode esse script de novo toda vez que alterar o código, antes de distribuir:
ele sempre remonta `dist/` do zero a partir da versão atual.
