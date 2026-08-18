"""Configuracao e persistencia dos dados de conexao com o banco de dados."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

CAMINHO_PADRAO = Path(__file__).resolve().parent.parent / "conexao.json"


@dataclass
class ConfiguracaoConexao:
    """Dados necessarios para conectar num banco MySQL/MariaDB."""

    host: str = "127.0.0.1"
    porta: str = "3306"
    usuario: str = "root"
    senha: str = ""
    banco: str = ""

    def url_sqlalchemy(self, incluir_banco: bool = True) -> str:
        """Monta a URL de conexao. Com incluir_banco=False, conecta no servidor
        sem selecionar nenhum banco especifico, usado pra checar/criar o banco
        antes dele existir."""
        nome_banco = self.banco if incluir_banco else ""
        return (
            f"mysql+pymysql://{self.usuario}:{self.senha}"
            f"@{self.host}:{self.porta}/{nome_banco}?charset=utf8mb4"
        )

    def esta_completa(self) -> bool:
        """Dados minimos pra tentar conectar no servidor (o banco em si e'
        tratado a parte, podendo ser criado se nao existir)."""
        return all([self.host, self.porta, self.usuario])


def carregar(caminho: Path = CAMINHO_PADRAO) -> ConfiguracaoConexao:
    """Recupera a ultima conexao salva neste computador, ou uma configuracao vazia."""
    if caminho.exists():
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        return ConfiguracaoConexao(**dados)
    return ConfiguracaoConexao()


def salvar(config: ConfiguracaoConexao, caminho: Path = CAMINHO_PADRAO) -> None:
    """Grava a conexao localmente, pra nao precisar redigitar da proxima vez."""
    caminho.write_text(
        json.dumps(asdict(config), ensure_ascii=False, indent=2), encoding="utf-8"
    )
