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
from .textos import Dialogos, Janela, SecaoConexao, SecaoLog, SecaoPlanilha, SeletorArquivo

_ICONE = Path(__file__).resolve().parent / "icone.ico"


class JanelaImportador(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(Janela.TITULO)
        self.geometry("640x560")
        self.resizable(False, False)
        self._aplicar_icone()

        self._fila_log: "queue.Queue[str]" = queue.Queue()
        self._caminho_planilha = tk.StringVar()

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

    # montagem da tela

    def _montar_secao_conexao(self) -> None:
        quadro = ttk.LabelFrame(self, text=SecaoConexao.TITULO, padding=10)
        quadro.pack(fill="x", padx=10, pady=(10, 5))

        self._var_host = tk.StringVar()
        self._var_porta = tk.StringVar()
        self._var_usuario = tk.StringVar()
        self._var_senha = tk.StringVar()
        self._var_banco = tk.StringVar()

        campos = [
            (SecaoConexao.ROTULO_HOST, self._var_host),
            (SecaoConexao.ROTULO_PORTA, self._var_porta),
            (SecaoConexao.ROTULO_USUARIO, self._var_usuario),
            (SecaoConexao.ROTULO_SENHA, self._var_senha),
            (SecaoConexao.ROTULO_BANCO, self._var_banco),
        ]
        for i, (rotulo, variavel) in enumerate(campos):
            ttk.Label(quadro, text=rotulo).grid(row=i, column=0, sticky="w", pady=3)
            mostrar = "*" if rotulo == SecaoConexao.ROTULO_SENHA else ""
            ttk.Entry(quadro, textvariable=variavel, show=mostrar, width=40).grid(
                row=i, column=1, sticky="we", padx=(8, 0), pady=3
            )
        quadro.columnconfigure(1, weight=1)

        ttk.Button(quadro, text=SecaoConexao.BOTAO_TESTAR, command=self._testar_conexao).grid(
            row=len(campos), column=0, columnspan=2, pady=(8, 0), sticky="we"
        )

    def _montar_secao_planilha(self) -> None:
        quadro = ttk.LabelFrame(self, text=SecaoPlanilha.TITULO, padding=10)
        quadro.pack(fill="x", padx=10, pady=5)

        linha = ttk.Frame(quadro)
        linha.pack(fill="x")
        ttk.Button(
            linha, text=SecaoPlanilha.BOTAO_SELECIONAR, command=self._selecionar_planilha
        ).pack(side="left")
        ttk.Label(linha, textvariable=self._caminho_planilha, foreground="#555").pack(
            side="left", padx=8
        )

        linha2 = ttk.Frame(quadro)
        linha2.pack(fill="x", pady=(10, 0))
        ttk.Label(linha2, text=SecaoPlanilha.ROTULO_TABELA).pack(side="left")
        self._var_tabela = tk.StringVar()
        ttk.Entry(linha2, textvariable=self._var_tabela, width=30).pack(
            side="left", padx=8, fill="x", expand=True
        )

        linha3 = ttk.Frame(quadro)
        linha3.pack(fill="x", pady=(10, 0))
        self._var_modo = tk.StringVar(value=ModoImportacao.SUBSTITUIR.value)
        ttk.Radiobutton(
            linha3, text=SecaoPlanilha.OPCAO_SUBSTITUIR, variable=self._var_modo,
            value=ModoImportacao.SUBSTITUIR.value,
        ).pack(anchor="w")
        ttk.Radiobutton(
            linha3, text=SecaoPlanilha.OPCAO_ADICIONAR,
            variable=self._var_modo, value=ModoImportacao.ADICIONAR.value,
        ).pack(anchor="w")

        ttk.Button(quadro, text=SecaoPlanilha.BOTAO_IMPORTAR, command=self._iniciar_importacao).pack(
            pady=(12, 0), fill="x"
        )

    def _montar_secao_log(self) -> None:
        quadro = ttk.LabelFrame(self, text=SecaoLog.TITULO, padding=10)
        quadro.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        self._texto_log = tk.Text(quadro, height=12, state="disabled", wrap="word")
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
            self._log(f"ERRO: {banco.mensagem_amigavel(erro)}")


def executar() -> None:
    app = JanelaImportador()
    app.mainloop()
