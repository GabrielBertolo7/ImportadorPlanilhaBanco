# Importador de Planilhas para Banco de Dados: Guia de Uso

Ferramenta para pegar uma planilha (Excel ou CSV) e jogar os dados dela direto
num banco de dados MySQL/MariaDB, sem precisar escrever nenhum código.

## O que você precisa ter em mãos antes de usar

- O arquivo da planilha (`.xlsx`, `.xls` ou `.csv`).
- Os dados de acesso ao banco de dados: **host** (endereço do servidor),
  **porta**, **usuário**, **senha** e **nome do banco de dados**. Peça isso pra
  quem administra o banco, se não souber.
- O nome da tabela onde os dados devem entrar (pode ser uma tabela que já
  existe, ou um nome novo: a ferramenta cria a tabela sozinha se ela não
  existir).

## Preciso instalar o MariaDB?

Só se **você** for quem está criando o banco de dados do zero. Nesse caso, sim,
é necessário ter um MariaDB (ou MySQL) instalado e rodando antes de usar esta
ferramenta.

Se o banco de dados **já existe** em algum servidor (compartilhado, de outro
cliente, etc.), você não precisa instalar nada disso, só precisa dos dados de
acesso (host, porta, usuário, senha, nome do banco) e de acesso de rede até
esse servidor. Esta ferramenta só **conecta** num banco já existente, ela não
instala nem cria o servidor de banco de dados.

**Importante:** esta ferramenta funciona com bancos **MySQL e MariaDB**
(mesmo "protocolo" de comunicação). Ela **não** funciona com outros tipos de
banco, como PostgreSQL, SQL Server ou Oracle; isso exigiria outra versão da
ferramenta.

## Primeira vez usando (instalação)

1. Copie a pasta inteira desta ferramenta para o computador (pode ser direto
   da pasta compartilhada da rede).
2. Dê **dois cliques** no arquivo **`Instalar Programa.bat`**.
   - Se o computador não tiver o Python instalado, essa etapa instala
     automaticamente (só aguarde, pode demorar alguns minutos). Quando
     terminar, ele vai pedir pra você fechar a janela e clicar em
     "Instalar Programa.bat" de novo: faça isso, é só pra continuar a instalação.
   - Se já tiver Python, ele só instala as bibliotecas necessárias.
3. Quando aparecer "Instalação concluída!", pode fechar a janela.

Isso só precisa ser feito **uma vez** em cada computador.

## Usando a ferramenta

1. Dê dois cliques em **`Importar Planilha.bat`**. Vai abrir uma janela do
   programa (sem janela preta de terminal).
2. Preencha os campos de **conexão com o banco de dados** (host, porta,
   usuário, senha, nome do banco). Da primeira vez que você clicar em "Testar
   conexão" ou em "Importar", esses dados ficam salvos no computador; nas
   próximas vezes já vêm preenchidos sozinhos.
3. Clique em **"Testar conexão"** para conferir se os dados estão certos antes
   de importar. Se der erro, revise host/porta/usuário/senha.
   - Se o **banco de dados** informado ainda não existir no servidor, a
     ferramenta pergunta se quer criar um novo banco com esse nome; clique em
     "Sim" pra ela criar automaticamente.
   - Se você deixar o campo **banco de dados em branco**, ela sugere criar um
     banco novo com um nome genérico (baseado na data/hora), útil quando o
     computador só tem o MariaDB instalado, sem nenhum banco criado ainda.
4. Clique em **"Selecionar planilha..."** e escolha o arquivo.
5. Digite o **nome da tabela de destino** (a ferramenta já sugere um nome
   baseado no nome do arquivo, mas você pode mudar).
6. Escolha uma das opções:
   - **Substituir dados existentes na tabela**: apaga tudo que já estava
     naquela tabela e recarrega do zero com a planilha.
   - **Adicionar aos dados existentes**: mantém o que já tem e só acrescenta
     as linhas da planilha.
7. Clique em **Importar** e acompanhe o progresso na caixa de texto embaixo.
   No final, ele confirma quantas linhas foram importadas.

## Perguntas comuns

**"Deu erro dizendo que não conseguiu conectar."**
Confira se host/porta/usuário/senha/banco estão certos, e se o computador tem
acesso de rede até o servidor do banco (às vezes é preciso estar conectado na
rede da empresa ou VPN).

**"A planilha está aberta no Excel, dá problema?"**
Feche o arquivo no Excel antes de importar: com o arquivo aberto, às vezes o
Windows não deixa outro programa ler ele.

**"Os nomes das colunas na planilha têm espaço, acento, letra maiúscula, tem
problema?"**
Não. A ferramenta ajusta automaticamente os nomes das colunas para um formato
válido de banco de dados (tudo minúsculo, sem espaço/acento/símbolo) na hora de
criar ou comparar com a tabela.

**"Como a ferramenta decide se uma coluna vira número, data ou texto?"**
Ela olha todos os valores da coluna inteira e só assume número ou data quando
**tem certeza absoluta** de que nenhum valor vai ser alterado ou perdido:
- Vira **número inteiro** só se todos os valores forem dígitos limpos (sem
  zero à esquerda tipo CEP/código, e sem serem grandes demais).
- Vira **decimal** só se todos os valores forem números com casas decimais
  consistentes.
- Vira **data** ou **data e hora** só se todos os valores da coluna baterem
  com um formato de data reconhecido.
- Em qualquer outro caso (mistura de texto e número, zero à esquerda, número
  gigante tipo chave de NF-e, formato de data inconsistente etc.), a coluna
  fica como **texto**, preservando o valor exatamente como veio da planilha.

Isso significa que, ao reimportar uma planilha numa tabela que já existe com
colunas em texto, a ferramenta pode **corrigir o tipo da coluna** para o tipo
certo, mas só quando a opção escolhida for "Substituir dados existentes"
(porque aí a tabela fica vazia antes da alteração, sem risco). No modo
"Adicionar", os tipos das colunas já existentes não são mexidos, só os dados
são inseridos.

**"Depois de importar, aparecem umas linhas no log falando de 'Índice criado'. O que é isso?"**
A ferramenta cria automaticamente um índice (uma espécie de atalho de busca,
que deixa consultas e junções entre tabelas mais rápidas) nas colunas que
parecem ser identificador: a coluna `id` (se os valores forem únicos) e
qualquer coluna terminada em `_id`. Isso não altera nenhum dado, só ajuda o
banco a trabalhar mais rápido, inclusive é importante pra quando essas
tabelas forem usadas numa ferramenta de BI. Se não der pra criar algum índice
por algum motivo, ela avisa no log e segue em frente normalmente.

**"Rodei duas vezes sem querer no modo 'Substituir', perdi dado?"**
Não tem problema: "Substituir" sempre recarrega a partir da planilha
selecionada, então rodar de novo com a mesma planilha resulta na mesma tabela.
O que se perde é qualquer dado que **não veio da planilha** e tinha sido
colocado manualmente na tabela antes; por isso a ferramenta pede confirmação
antes de substituir.
