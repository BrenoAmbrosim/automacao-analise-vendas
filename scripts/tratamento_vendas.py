import pandas as pd
from pathlib import Path


# Caminhos do projeto

BASE_DIR = Path(__file__).resolve().parent.parent
ARQUIVO_ENTRADA = BASE_DIR / "dados_brutos" / "vendas_loja.xlsx"
ARQUIVO_SAIDA = BASE_DIR / "dados_tratados" / "vendas_tratadas.csv"


# Leitura do Excel

df = pd.read_excel(
    ARQUIVO_ENTRADA,
    sheet_name="vendas_brutas",
    header=3
)

print("Linhas originais:", len(df))
print("Colunas encontradas:", list(df.columns))


# Padronização básica

df.columns = df.columns.str.strip().str.lower()
df = df.dropna(how="all")


# Limpeza inicial de texto

colunas_texto = ["produto", "vendedor", "cidade"]

for col in colunas_texto:
    if col in df.columns:
        df[col] = df[col].astype("string").str.strip()
        df[col] = df[col].replace({"nan": pd.NA, "None": pd.NA, "": pd.NA})


# Tratamento de data

df["data"] = pd.to_datetime(df["data"], errors="coerce", dayfirst=True)

# remover datas inválidas
df = df.dropna(subset=["data"])


# Tratamento de quantidade

df["quantidade"] = (
    df["quantidade"]
    .astype("string")
    .str.strip()
    .str.extract(r"(\d+)", expand=False)
)

df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce")

# quantidade vazia vira 1
df["quantidade"] = df["quantidade"].fillna(1)

# remover quantidade zero ou negativa
df = df[df["quantidade"] > 0]


# Tratamento de preço

df["preco_unitario"] = (
    df["preco_unitario"]
    .astype("string")
    .str.strip()
    .str.replace("R$", "", regex=False)
)

# converte direto para número
df["preco_unitario"] = pd.to_numeric(df["preco_unitario"], errors="coerce")

# remover preços inválidos
df = df[df["preco_unitario"] > 0]

# arredondar preço para 2 casas
df["preco_unitario"] = df["preco_unitario"].round(2)


# Preenchimento de vazios

df["vendedor"] = df["vendedor"].fillna("Não informado")
df["cidade"] = df["cidade"].fillna("Não informada")
df["produto"] = df["produto"].fillna("Não informado")


# Padronização de texto

df["produto"] = df["produto"].str.lower().str.strip()
df["vendedor"] = df["vendedor"].str.title().str.strip()
df["cidade"] = df["cidade"].str.upper().str.strip()


# Remover duplicados

df = df.drop_duplicates()


# Criar faturamento

df["faturamento"] = (df["quantidade"] * df["preco_unitario"]).round(2)


# Ajustes finais

df = df.sort_values(by="data").reset_index(drop=True)


# Salvar CSV tratado

ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8-sig")

print("Linhas finais:", len(df))
print("Arquivo salvo em:", ARQUIVO_SAIDA)
print("\nPrévia dos dados tratados:")
print(df.head())