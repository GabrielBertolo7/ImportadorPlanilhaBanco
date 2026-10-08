"""Interface grafica (Tkinter) do Importador de Planilhas para Banco de Dados."""
from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from . import banco
from . import config as config_modulo
from . import servico
from .config import ConfiguracaoConexao
from .planilha import normalizar_nome_coluna
from .servico import ModoImportacao
from .textos import Dialogos, Janela, Progresso, SecaoConexao, SecaoLog, SecaoPlanilha, SeletorArquivo

_ICONE = Path(__file__).resolve().parent / "icone.ico"


# Paleta e fontes da interface (claro, sobrio, um unico tom de destaque).
_COR_FUNDO = "#F4F6F8"
_COR_CARTAO = "#FFFFFF"
_COR_BORDA = "#E5E7EB"
_COR_BORDA_CAMPO = "#D1D5DB"
_COR_TEXTO = "#111827"
_COR_SUAVE = "#6B7280"
_COR_DESTAQUE = "#1D4ED8"
_COR_DESTAQUE_ESCURO = "#1E40AF"
_COR_DESTAQUE_CLARO = "#DBEAFE"
_FONTE = "Segoe UI"
_FONTE_LOG = ("Cascadia Mono", 9)


class JanelaImportador(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(Janela.TITULO)
        self.geometry("720x840")
        self.minsize(640, 720)
        self.configure(background=_COR_FUNDO)
        self._aplicar_icone()
        self._configurar_estilo()

        self._fila_log: "queue.Queue[str]" = queue.Queue()
        self._caminho_planilha = tk.StringVar()
        self._rotulo_planilha = tk.StringVar(value=SecaoPlanilha.NENHUMA_PLANILHA)

        self._montar_cabecalho()
        self._montar_secao_conexao()
        self._montar_secao_planilha()
        self._montar_secao_log()

        self._carregar_conexao_salva()
        self.after(150, self._drenar_fila_log)

    def _aplicar_icone(self) -> None:
        if _ICONE.exists():
            try:
                self.iconbitmap(str(_ICONE))
            except tk.TclError:
                pass  # icone e' so estetico, nao vale travar o programa por causa dele

    def _configurar_estilo(self) -> None:
        estilo = ttk.Style(self)
        estilo.theme_use("clam")

        estilo.configure(".", font=(_FONTE, 10), background=_COR_CARTAO, foreground=_COR_TEXTO)
        estilo.configure("Fundo.TFrame", background=_COR_FUNDO)
        estilo.configure("Cartao.TFrame", background=_COR_CARTAO)
        estilo.configure("Rotulo.TLabel", background=_COR_CARTAO, foreground=_COR_SUAVE, font=(_FONTE, 9, "bold"))
        estilo.configure("Arquivo.TLabel", background=_COR_CARTAO, foreground=_COR_SUAVE)
        estilo.configure("TituloCartao.TLabel", background=_COR_CARTAO, foreground=_COR_TEXTO,
                         font=(_FONTE, 11, "bold"))
        estilo.configure("Passo.TLabel", background=_COR_DESTAQUE_CLARO, foreground=_COR_DESTAQUE,
                         font=(_FONTE, 9, "bold"), padding=(7, 1), anchor="center")
        estilo.configure("Titulo.TLabel", background=_COR_FUNDO, foreground=_COR_TEXTO, font=(_FONTE, 16, "bold"))
        estilo.configure("Subtitulo.TLabel", background=_COR_FUNDO, foreground=_COR_SUAVE, font=(_FONTE, 10))

        estilo.configure("TEntry", padding=(8, 6), fieldbackground="#FFFFFF", bordercolor=_COR_BORDA_CAMPO,
                         lightcolor=_COR_BORDA_CAMPO, darkcolor=_COR_BORDA_CAMPO)
        estilo.map("TEntry", bordercolor=[("focus", _COR_DESTAQUE)], lightcolor=[("focus", _COR_DESTAQUE)],
                   darkcolor=[("focus", _COR_DESTAQUE)])

        estilo.configure("TRadiobutton", background=_COR_CARTAO, foreground=_COR_TEXTO, padding=(0, 3))
        estilo.map("TRadiobutton", background=[("active", _COR_CARTAO)],
                   indicatorcolor=[("selected", _COR_DESTAQUE), ("!selected", "#FFFFFF")])

        estilo.configure("Principal.TButton", background=_COR_DESTAQUE, foreground="#FFFFFF",
                         bordercolor=_COR_DESTAQUE, lightcolor=_COR_DESTAQUE, darkcolor=_COR_DESTAQUE,
                         focuscolor=_COR_DESTAQUE, font=(_FONTE, 10, "bold"), padding=(16, 9))
        estilo.map("Principal.TButton",
                   background=[("active", _COR_DESTAQUE_ESCURO), ("pressed", _COR_DESTAQUE_ESCURO)],
                   bordercolor=[("active", _COR_DESTAQUE_ESCURO)])
        estilo.configure("Secundario.TButton", background="#FFFFFF", foreground=_COR_TEXTO,
                         bordercolor=_COR_BORDA_CAMPO, lightcolor="#FFFFFF", darkcolor="#FFFFFF",
                         focuscolor="#FFFFFF", font=(_FONTE, 10, "bold"), padding=(14, 7))
        estilo.map("Secundario.TButton", background=[("active", "#F3F4F6"), ("pressed", "#E5E7EB")])

    # montagem da tela

    def _montar_cabecalho(self) -> None:
        cabecalho = ttk.Frame(self, style="Fundo.TFrame", padding=(22, 18, 22, 6))
        cabecalho.pack(fill="x")
        ttk.Label(cabecalho, text=Janela.TITULO, style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(cabecalho, text=Janela.SUBTITULO, style="Subtitulo.TLabel").pack(anchor="w", pady=(2, 0))

    def _criar_cartao(self, numero: str, titulo: str, expandir: bool = False) -> ttk.Frame:
        """Cartao branco com borda fina e titulo numerado (1, 2, 3: a ordem de uso)."""
        moldura = tk.Frame(self, background=_COR_CARTAO, highlightthickness=1,
                           highlightbackground=_COR_BORDA, highlightcolor=_COR_BORDA)
        moldura.pack(fill="both" if expandir else "x", expand=expandir, padx=20,
                     pady=(10, 20 if expandir else 0))
        conteudo = ttk.Frame(moldura, style="Cartao.TFrame", padding=(18, 14, 18, 16))
        conteudo.pack(fill="both", expand=True)

        titulo_linha = ttk.Frame(conteudo, style="Cartao.TFrame")
        titulo_linha.pack(fill="x", pady=(0, 10))
        ttk.Label(titulo_linha, text=numero, style="Passo.TLabel").pack(side="left")
        ttk.Label(titulo_linha, text=titulo, style="TituloCartao.TLabel").pack(side="left", padx=(10, 0))
        return conteudo

    @staticmethod
    def _rotulo(pai: tk.Misc, texto: str) -> ttk.Label:
        return ttk.Label(pai, text=texto.rstrip(":"), style="Rotulo.TLabel")

    def _montar_secao_conexao(self) -> None:
        quadro = self._criar_cartao("1", SecaoConexao.TITULO)
        grade = ttk.Frame(quadro, style="Cartao.TFrame")
        grade.pack(fill="x")
        grade.columnconfigure(0, weight=3, uniform="col")
        grade.columnconfigure(1, weight=2, uniform="col")

        self._var_host = tk.StringVar()
        self._var_porta = tk.StringVar()
        self._var_usuario = tk.StringVar()
        self._var_senha = tk.StringVar()
        self._var_banco = tk.StringVar()

        pares = [
            ((SecaoConexao.ROTULO_HOST, self._var_host, ""), (SecaoConexao.ROTULO_PORTA, self._var_porta, "")),
            ((SecaoConexao.ROTULO_USUARIO, self._var_usuario, ""),
             (SecaoConexao.ROTULO_SENHA, self._var_senha, "*")),
        ]
        for linha, par in enumerate(pares):
            for coluna, (rotulo, variavel, mostrar) in enumerate(par):
                espaco = (0, 10) if coluna == 0 else (0, 0)
                self._rotulo(grade, rotulo).grid(row=linha * 2, column=coluna, sticky="w", padx=espaco, pady=(4, 3))
                ttk.Entry(grade, textvariable=variavel, show=mostrar).grid(
                    row=linha * 2 + 1, column=coluna, sticky="we", padx=espaco
                )

        self._rotulo(grade, SecaoConexao.ROTULO_BANCO).grid(row=4, column=0, sticky="w", padx=(0, 10), pady=(4, 3))
        ttk.Entry(grade, textvariable=self._var_banco).grid(row=5, column=0, sticky="we", padx=(0, 10))
        ttk.Button(
            grade, text=SecaoConexao.BOTAO_TESTAR, style="Secundario.TButton", command=self._testar_conexao
        ).grid(row=5, column=1, sticky="we")

    def _montar_secao_planilha(self) -> None:
        quadro = self._criar_cartao("2", SecaoPlanilha.TITULO)

        linha = ttk.Frame(quadro, style="Cartao.TFrame")
        linha.pack(fill="x")
        ttk.Button(
            linha, text=SecaoPlanilha.BOTAO_SELECIONAR, style="Secundario.TButton",
            command=self._selecionar_planilha,
        ).pack(side="left")
        ttk.Label(linha, textvariable=self._rotulo_planilha, style="Arquivo.TLabel").pack(side="left", padx=12)

        self._rotulo(quadro, SecaoPlanilha.ROTULO_TABELA).pack(anchor="w", pady=(14, 3))
        self._var_tabela = tk.StringVar()
        ttk.Entry(quadro, textvariable=self._var_tabela).pack(fill="x")

        opcoes = ttk.Frame(quadro, style="Cartao.TFrame")
        opcoes.pack(fill="x", pady=(10, 0))
        self._var_modo = tk.StringVar(value=ModoImportacao.SUBSTITUIR.value)
        ttk.Radiobutton(
            opcoes, text=SecaoPlanilha.OPCAO_SUBSTITUIR, variable=self._var_modo,
            value=ModoImportacao.SUBSTITUIR.value,
        ).pack(anchor="w")
        ttk.Radiobutton(
            opcoes, text=SecaoPlanilha.OPCAO_ADICIONAR,
            variable=self._var_modo, value=ModoImportacao.ADICIONAR.value,
        ).pack(anchor="w")

        ttk.Button(
            quadro, text=SecaoPlanilha.BOTAO_IMPORTAR, style="Principal.TButton", command=self._iniciar_importacao
        ).pack(pady=(14, 0), fill="x")

    def _montar_secao_log(self) -> None:
        quadro = self._criar_cartao("3", SecaoLog.TITULO, expandir=True)
        self._texto_log = tk.Text(
            quadro, height=8, state="disabled", wrap="word", font=_FONTE_LOG,
            background="#F9FAFB", foreground="#1F2937", relief="flat", padx=12, pady=10,
            highlightthickness=1, highlightbackground=_COR_BORDA, highlightcolor=_COR_BORDA,
        )
        self._texto_log.pack(fill="both", expand=True)

    # estado / conexao

    def _configuracao_atual(self) -> ConfiguracaoConexao:
        return ConfiguracaoConexao(
            host=self._var_host.get().strip(),
            porta=self._var_porta.get().strip(),
            usuario=self._var_usuario.get().strip(),
            senha=self._var_senha.get(),
            banco=self._var_banco.get().strip(),
        )

    def _carregar_conexao_salva(self) -> None:
        self._aplicar_configuracao(config_modulo.carregar(), salvar=False)

    def _aplicar_configuracao(self, config: ConfiguracaoConexao, salvar: bool = True) -> None:
        """Reflete a configuracao nos campos da tela e, por padrao, ja salva
        localmente (usado depois de testar a conexao ou de criar um banco)."""
        self._var_host.set(config.host)
        self._var_porta.set(config.porta)
        self._var_usuario.set(config.usuario)
        self._var_senha.set(config.senha)
        self._var_banco.set(config.banco)
        if salvar:
            config_modulo.salvar(config)

    # acoes

    def _selecionar_planilha(self) -> None:
        caminho = filedialog.askopenfilename(
            title=SeletorArquivo.TITULO,
            filetypes=[
                (SeletorArquivo.FILTRO_PLANILHAS, "*.xlsx *.xls *.csv"),
                (SeletorArquivo.FILTRO_TODOS, "*.*"),
            ],
        )
        if caminho:
            self._caminho_planilha.set(caminho)
            self._rotulo_planilha.set(Path(caminho).name)
            if not self._var_tabela.get():
                self._var_tabela.set(normalizar_nome_coluna(Path(caminho).stem))

    def _log(self, mensagem: str) -> None:
        self._fila_log.put(mensagem)

    def _drenar_fila_log(self) -> None:
        try:
            while True:
                mensagem = self._fila_log.get_nowait()
                self._texto_log.configure(state="normal")
                self._texto_log.insert("end", mensagem + "\n")
                self._texto_log.see("end")
                self._texto_log.configure(state="disabled")
        except queue.Empty:
            pass
        self.after(150, self._drenar_fila_log)

    def _garantir_banco_existe(self, config: ConfiguracaoConexao) -> Optional[ConfiguracaoConexao]:
        """Confere se o banco existe no servidor. Se nao existir (ou nao tiver
        sido informado), pergunta se quer criar. Retorna a configuracao pronta
        pra usar (com o nome do banco preenchido), ou None se deve cancelar.

        Confirma a autenticacao no servidor ANTES de perguntar sobre criar um
        banco novo, senao a pergunta apareceria mesmo com host/usuario/senha
        errados, e um "Nao" nela sairia sem nunca avisar do erro de verdade."""
        banco.testar_conexao_servidor(config)

        if not config.banco:
            nome_sugerido = banco.gerar_nome_banco_generico()
            if not messagebox.askyesno(
                Dialogos.BANCO_NAO_INFORMADO, Dialogos.criar_banco_generico(nome_sugerido)
            ):
                return None
            config = ConfiguracaoConexao(**{**config.__dict__, "banco": nome_sugerido})
            banco.criar_banco(config)
            return config

        if banco.banco_existe(config):
            return config

        if not messagebox.askyesno(
            Dialogos.BANCO_NAO_ENCONTRADO, Dialogos.criar_banco_inexistente(config.banco)
        ):
            return None
        banco.criar_banco(config)
        return config

    def _testar_conexao(self) -> None:
        config = self._configuracao_atual()
        if not config.esta_completa():
            messagebox.showwarning(Dialogos.ATENCAO, Dialogos.PREENCHA_DADOS_BANCO)
            return
        try:
            config = self._garantir_banco_existe(config)
            if config is None:
                return
            banco.testar_conexao(config)
            self._aplicar_configuracao(config)
            messagebox.showinfo(Dialogos.CONEXAO, Dialogos.CONECTOU_COM_SUCESSO)
        except Exception as erro:  # noqa: BLE001 - erro de conexao e' esperado e mostrado ao usuario
            messagebox.showerror(
                Dialogos.CONEXAO, Dialogos.erro_conexao(banco.mensagem_amigavel(erro))
            )

    def _iniciar_importacao(self) -> None:
        config = self._configuracao_atual()
        caminho = self._caminho_planilha.get()
        tabela = self._var_tabela.get().strip()
        modo = ModoImportacao(self._var_modo.get())

        if not caminho:
            messagebox.showwarning(Dialogos.ATENCAO, Dialogos.SELECIONE_PLANILHA)
            return
        if not tabela:
            messagebox.showwarning(Dialogos.ATENCAO, Dialogos.INFORME_TABELA)
            return
        if not config.esta_completa():
            messagebox.showwarning(Dialogos.ATENCAO, Dialogos.PREENCHA_DADOS_BANCO)
            return

        try:
            config = self._garantir_banco_existe(config)
        except Exception as erro:  # noqa: BLE001 - mostrado ao usuario, nao tecnico
            messagebox.showerror(
                Dialogos.CONEXAO, Dialogos.erro_conexao_servidor(banco.mensagem_amigavel(erro))
            )
            return
        if config is None:
            return

        if modo is ModoImportacao.SUBSTITUIR and not messagebox.askyesno(
            Dialogos.CONFIRMAR, Dialogos.confirmar_substituicao(tabela)
        ):
            return

        self._aplicar_configuracao(config)
        threading.Thread(
            target=self._executar_importacao, args=(config, caminho, tabela, modo), daemon=True
        ).start()

    def _executar_importacao(
        self, config: ConfiguracaoConexao, caminho: str, tabela: str, modo: ModoImportacao
    ) -> None:
        try:
            self._log("=" * 60)
            servico.importar(config, caminho, tabela, modo, log=self._log)
        except Exception as erro:  # noqa: BLE001 - mostrado no log pro usuario final, nao tecnico
            self._log(f"{Progresso.ERRO}: {banco.mensagem_amigavel(erro)}")


def executar() -> None:
    app = JanelaImportador()
    app.mainloop()
