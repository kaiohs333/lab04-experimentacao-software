"""
Coleta dados do Bolsa Família via API do Portal da Transparência.

Estratégia:
- Snapshot (Dez/2023): todos os ~5.570 municípios → RQ1, RQ3, RQ4
- Histórico: todos os meses de 2023 + Dezembro de 2019-2022 apenas para capitais estaduais → RQ2
"""

import requests
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"
HEADERS = {"chave-api-dados": API_KEY, "Accept": "application/json"}

# Endpoint correto por período histórico do programa:
# 2019-2020        → Bolsa Família
# 2021 - Fev/2023  → Auxílio Brasil
# Mar/2023+        → Novo Bolsa Família
def get_endpoint(periodo: str) -> str:
    ano = int(periodo[:4])
    mes = int(periodo[4:])
    if ano <= 2020:
        return "bolsa-familia-por-municipio"
    elif ano <= 2022 or (ano == 2023 and mes <= 2):
        return "auxilio-brasil-por-municipio"
    else:
        return "novo-bolsa-familia-por-municipio"

# Capitais estaduais e seus códigos IBGE
STATE_CAPITALS = {
    "AC": ("Rio Branco",       "1200401"),
    "AL": ("Maceió",           "2704302"),
    "AM": ("Manaus",           "1302603"),
    "AP": ("Macapá",           "1600303"),
    "BA": ("Salvador",         "2927408"),
    "CE": ("Fortaleza",        "2304400"),
    "DF": ("Brasília",         "5300108"),
    "ES": ("Vitória",          "3205309"),
    "GO": ("Goiânia",          "5208707"),
    "MA": ("São Luís",         "2111300"),
    "MG": ("Belo Horizonte",   "3106200"),
    "MS": ("Campo Grande",     "5002704"),
    "MT": ("Cuiabá",           "5103403"),
    "PA": ("Belém",            "1501402"),
    "PB": ("João Pessoa",      "2507507"),
    "PE": ("Recife",           "2611606"),
    "PI": ("Teresina",         "2211001"),
    "PR": ("Curitiba",         "4106902"),
    "RJ": ("Rio de Janeiro",   "3304557"),
    "RN": ("Natal",            "2408102"),
    "RO": ("Porto Velho",      "1100205"),
    "RR": ("Boa Vista",        "1400100"),
    "RS": ("Porto Alegre",     "4314902"),
    "SC": ("Florianópolis",    "4205407"),
    "SE": ("Aracaju",          "2800308"),
    "SP": ("São Paulo",        "3550308"),
    "TO": ("Palmas",           "1721000"),
}

# Dezembro de cada ano para comparação histórica (apenas capitais)
YEARLY_DEC = ["201912", "202012", "202112", "202212"]

# Todos os meses de 2023 (apenas capitais)
MONTHLY_2023 = [f"2023{str(m).zfill(2)}" for m in range(1, 13)]

# Snapshot completo de Dezembro/2023 (todos os municípios)
SNAPSHOT_PERIOD = "202312"


def fetch_municipality(ibge_code: str, periodo: str, retries: int = 4) -> dict | None:
    """Busca dados de um município em um período específico, com retry."""
    endpoint = get_endpoint(periodo)
    for attempt in range(retries):
        try:
            r = requests.get(
                f"{BASE_URL}/{endpoint}",
                headers=HEADERS,
                params={"mesAno": periodo, "codigoIbge": ibge_code, "pagina": 1},
                timeout=20,
            )
            if r.status_code == 200:
                data = r.json()
                return data[0] if data else None
            elif r.status_code == 429:
                wait = 10 * (attempt + 1)
                print(f"  [Rate limit] Aguardando {wait}s...")
                time.sleep(wait)
            else:
                return None
        except requests.RequestException as e:
            if attempt < retries - 1:
                time.sleep(3)
    return None


def collect_capitals_for_period(periodo: str) -> list:
    """Coleta dados das 27 capitais para um período (sequencial com delay)."""
    results = []
    for uf, (nome_capital, ibge) in STATE_CAPITALS.items():
        record = fetch_municipality(ibge, periodo)
        if record:
            results.append(record)
        time.sleep(0.5)  # conservador para evitar rate limiting
    return results


def get_all_ibge_codes() -> list[str]:
    """Busca todos os códigos IBGE de municípios via API do IBGE."""
    print("Buscando códigos IBGE de todos os municípios...")
    r = requests.get(
        "https://servicodados.ibge.gov.br/api/v1/localidades/municipios",
        timeout=30,
    )
    municipios = r.json()
    codes = [str(m["id"]) for m in municipios]
    print(f"  {len(codes)} municípios encontrados.")
    return codes


def collect_snapshot_all_municipalities(ibge_codes: list[str]) -> list:
    """Coleta dados de TODOS os municípios para o período de snapshot (paralelo)."""
    results = []
    failed = []
    total = len(ibge_codes)

    def fetch(code):
        return fetch_municipality(code, SNAPSHOT_PERIOD)

    print(f"Coletando snapshot de {SNAPSHOT_PERIOD} para {total} municípios (paralelo, pode levar ~15 min)...")
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch, code): code for code in ibge_codes}
        done = 0
        for future in as_completed(futures):
            done += 1
            result = future.result()
            if result:
                results.append(result)
            else:
                failed.append(futures[future])
            if done % 500 == 0:
                print(f"  {done}/{total} ({len(results)} com dados)")

    print(f"  Concluído: {len(results)} registros | {len(failed)} sem dados")
    return results


def save(data: list, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    os.makedirs("data/raw", exist_ok=True)

    # ── 1. Snapshot: todos os municípios, Dez/2023 ──────────────────────────
    snapshot_file = f"data/raw/snapshot_{SNAPSHOT_PERIOD}_all.json"
    if os.path.exists(snapshot_file):
        print(f"[SKIP] Snapshot {SNAPSHOT_PERIOD} já existe.")
    else:
        ibge_codes = get_all_ibge_codes()
        data = collect_snapshot_all_municipalities(ibge_codes)
        save(data, snapshot_file)
        print(f"Snapshot salvo: {len(data)} registros\n")

    # ── 2. Capitais: todos os meses de 2023 ─────────────────────────────────
    for periodo in MONTHLY_2023:
        output = f"data/raw/capitais_{periodo}.json"
        if os.path.exists(output) and os.path.getsize(output) > 5:
            print(f"[SKIP] Capitais {periodo} já existem.")
            continue
        print(f"[COLETANDO] Capitais {periodo}...")
        data = collect_capitals_for_period(periodo)
        save(data, output)
        print(f"  {len(data)} capitais salvas.\n")

    # ── 3. Capitais: Dezembro de 2019–2022 ───────────────────────────────────
    for periodo in YEARLY_DEC:
        output = f"data/raw/capitais_{periodo}.json"
        if os.path.exists(output) and os.path.getsize(output) > 5:
            print(f"[SKIP] Capitais {periodo} já existem.")
            continue
        print(f"[COLETANDO] Capitais Dez/{periodo[:4]}...")
        data = collect_capitals_for_period(periodo)
        save(data, output)
        print(f"  {len(data)} capitais salvas.\n")

    print("\nColeta concluída! Arquivos em data/raw/")


if __name__ == "__main__":
    main()
