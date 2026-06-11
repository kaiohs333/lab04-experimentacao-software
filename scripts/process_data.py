"""
Processa dados brutos do Bolsa Família e gera CSVs prontos para o BI.

Arquivos de entrada (data/raw/):
  snapshot_202312_all.json    → todos os municípios, Dez/2023
  capitais_AAAAMM.json        → 27 capitais, múltiplos períodos

Saídas (data/processed/):
  caracterizacao_dataset.csv      → visão geral do dataset
  rq1_beneficiarios_por_estado.csv
  rq2_evolucao_anual_capitais.csv
  rq2_evolucao_mensal_2023.csv
  rq3_media_por_regiao.csv
  rq4_top_municipios.csv
"""

import json
import os
import glob
import pandas as pd

REGIAO_MAP = {
    "AC": "Norte",      "AM": "Norte",      "AP": "Norte",
    "PA": "Norte",      "RO": "Norte",      "RR": "Norte",   "TO": "Norte",
    "AL": "Nordeste",   "BA": "Nordeste",   "CE": "Nordeste",
    "MA": "Nordeste",   "PB": "Nordeste",   "PE": "Nordeste",
    "PI": "Nordeste",   "RN": "Nordeste",   "SE": "Nordeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste",
    "MS": "Centro-Oeste", "MT": "Centro-Oeste",
    "ES": "Sudeste",    "MG": "Sudeste",    "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul",        "RS": "Sul",        "SC": "Sul",
}

NOME_MES = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
    5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}


def parse_record(record: dict, periodo: str) -> dict:
    """Normaliza um registro da API para um dict plano."""
    mun = record.get("municipio", {})
    uf_obj = mun.get("uf", {})
    return {
        "periodo":           periodo,
        "ano":               int(periodo[:4]),
        "mes":               int(periodo[4:]),
        "ibge":              mun.get("codigoIBGE", ""),
        "municipio":         mun.get("nomeIBGE", ""),
        "uf":                uf_obj.get("sigla", ""),
        "estado":            uf_obj.get("nome", ""),
        "regiao":            mun.get("nomeRegiao", ""),
        "programa":          record.get("tipo", {}).get("descricao", ""),
        "qtd_beneficiarios": record.get("quantidadeBeneficiados", 0) or 0,
        "valor":             record.get("valor", 0.0) or 0.0,
    }


def load_json(path: str, periodo: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [parse_record(r, periodo) for r in data if r]


def main():
    os.makedirs("data/processed", exist_ok=True)

    # ── Carrega snapshot (todos os municípios, Dez/2023) ─────────────────────
    snapshot_path = "data/raw/snapshot_202312_all.json"
    if not os.path.exists(snapshot_path):
        print("ERRO: Execute collect_data.py primeiro (snapshot não encontrado).")
        return

    print("Carregando snapshot Dez/2023...")
    df_snap = pd.DataFrame(load_json(snapshot_path, "202312"))
    print(f"  {len(df_snap):,} registros carregados.")

    # ── Carrega capitais (histórico) ──────────────────────────────────────────
    cap_files = sorted(glob.glob("data/raw/capitais_*.json"))
    cap_frames = []
    for path in cap_files:
        periodo = os.path.basename(path).replace("capitais_", "").replace(".json", "")
        cap_frames.append(pd.DataFrame(load_json(path, periodo)))

    df_cap = pd.concat(cap_frames, ignore_index=True) if cap_frames else pd.DataFrame()
    print(f"  {len(df_cap):,} registros de capitais carregados.\n")

    # ── Caracterização do dataset ─────────────────────────────────────────────
    print("Gerando: caracterizacao_dataset.csv")
    carac = df_snap.groupby(["uf", "estado", "regiao"]).agg(
        municipios       =("municipio", "nunique"),
        total_beneficiarios=("qtd_beneficiarios", "sum"),
        total_valor      =("valor", "sum"),
    ).reset_index()
    carac["valor_medio"] = (carac["total_valor"] / carac["total_beneficiarios"]).round(2)
    carac = carac.sort_values("total_beneficiarios", ascending=False)
    carac.to_csv("data/processed/caracterizacao_dataset.csv", index=False)

    # ── RQ1: Beneficiários por estado (Dez/2023) ──────────────────────────────
    print("Gerando: rq1_beneficiarios_por_estado.csv")
    carac.to_csv("data/processed/rq1_beneficiarios_por_estado.csv", index=False)

    # ── RQ2: Evolução anual — capitais (Dez de cada ano) ─────────────────────
    print("Gerando: rq2_evolucao_anual_capitais.csv")
    if not df_cap.empty:
        df_dec = df_cap[df_cap["mes"] == 12]
        rq2_anual = df_dec.groupby(["ano", "programa"]).agg(
            total_beneficiarios=("qtd_beneficiarios", "sum"),
            total_valor        =("valor", "sum"),
        ).reset_index()
        rq2_anual["valor_medio"] = (rq2_anual["total_valor"] / rq2_anual["total_beneficiarios"]).round(2)
        rq2_anual.to_csv("data/processed/rq2_evolucao_anual_capitais.csv", index=False)

    # ── RQ2: Evolução mensal — capitais 2023 ─────────────────────────────────
    print("Gerando: rq2_evolucao_mensal_2023.csv")
    if not df_cap.empty:
        df_2023 = df_cap[df_cap["ano"] == 2023]
        rq2_mensal = df_2023.groupby("mes").agg(
            total_beneficiarios=("qtd_beneficiarios", "sum"),
            total_valor        =("valor", "sum"),
        ).reset_index()
        rq2_mensal["nome_mes"] = rq2_mensal["mes"].map(NOME_MES)
        rq2_mensal["valor_medio"] = (rq2_mensal["total_valor"] / rq2_mensal["total_beneficiarios"]).round(2)
        rq2_mensal.to_csv("data/processed/rq2_evolucao_mensal_2023.csv", index=False)

    # ── RQ3: Valor médio por região (Dez/2023, todos os municípios) ───────────
    print("Gerando: rq3_media_por_regiao.csv")
    rq3 = df_snap.groupby("regiao").agg(
        estados             =("uf", "nunique"),
        municipios          =("municipio", "nunique"),
        total_beneficiarios =("qtd_beneficiarios", "sum"),
        total_valor         =("valor", "sum"),
    ).reset_index()
    rq3["valor_medio_por_beneficiario"] = (rq3["total_valor"] / rq3["total_beneficiarios"]).round(2)
    rq3 = rq3.sort_values("valor_medio_por_beneficiario", ascending=False)
    rq3.to_csv("data/processed/rq3_media_por_regiao.csv", index=False)

    # ── RQ4: Top 50 municípios (Dez/2023) ────────────────────────────────────
    print("Gerando: rq4_top_municipios.csv")
    rq4 = df_snap[["municipio", "uf", "regiao", "qtd_beneficiarios", "valor"]].copy()
    rq4["valor_medio"] = (rq4["valor"] / rq4["qtd_beneficiarios"]).round(2)
    rq4 = rq4.sort_values("qtd_beneficiarios", ascending=False).head(50)
    rq4.to_csv("data/processed/rq4_top_municipios.csv", index=False)

    # ── Resumo ────────────────────────────────────────────────────────────────
    print("\n=== Resumo do Dataset (Dez/2023 - todos os municípios) ===")
    print(f"  Estados analisados  : {carac['uf'].nunique()}")
    print(f"  Municípios          : {df_snap['municipio'].nunique():,}")
    print(f"  Total beneficiários : {carac['total_beneficiarios'].sum():,.0f}")
    print(f"  Total pago          : R$ {carac['total_valor'].sum():,.2f}")
    print("\nCSVs salvos em data/processed/")


if __name__ == "__main__":
    main()
