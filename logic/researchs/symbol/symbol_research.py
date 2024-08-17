import json
import pandas as pd
from typing import List
from logic.service import Service
from logic.researchs.base_research import BaseResearch


class SymbolResearch(BaseResearch):

    def __init__(self, service: Service):
        super().__init__(service)

    def analyze_symbols_full_list(self):
        # Load the stock list
        pd_symbols = pd.read_csv(self.config.FOLDER_Symbols / "FullSymbols.csv")

        # step 1. Filter by status
        pd_active_symbols = pd_symbols[pd_symbols['status'] == 'Active']
        # Step 2. Group by exchange and asset type
        pd_symbols_grouped = pd_active_symbols.groupby(['exchange', 'assetType'])
        # step 3. Export grouped data to separate lists
        pd_grouped_list = {name: group for name, group in pd_symbols_grouped}

        # Category 1.a Save symbols into separate csv files
        json_symbols = {'count': {
            'total_exchanges': len(pd_active_symbols["exchange"].unique()),
            'total_derivatives': len(pd_active_symbols["assetType"]),
        }}
        for name, group in pd_grouped_list.items():
            exchange = name[0]
            derivative = name[1]
            csv = self.engine.csv("symbols", "exchange", exchange, f"{derivative}.csv")
            csv.save_df(group)

            # Collect json_symbols information
            if exchange not in json_symbols:
                json_symbols[exchange] = {}
            total = len(group)
            json_symbols[exchange][derivative] = total

            # Ensure the dynamic key exists in json_symbols before adding the total
            if derivative not in json_symbols['count']:
                json_symbols['count'][derivative] = 0
            json_symbols['count'][derivative] += total
        # Category 1.b Symbols json_symbols
        self.engine.json_research("watch", "symbols_summary.json").save(json_symbols)

        # Category 2. Equity by Sector & Industry
        json_file_sector = self.path_exist(self.config.FOLDER_Watch / "symbols_sector.json")
        json_file_industry = self.path_exist(self.config.FOLDER_Watch / "symbols_industry.json")

        json_symbols_sector = {}
        json_symbols_industry = {}
        for json_file in (self.config.FOLDER_Infos / "EQUITY").glob("*.json"):
            with (open(json_file, "r")) as file:
                data = json.load(file)
                sector = data.get("sector", "Unknown")
                industry = data.get("industry", "Unknown")
                symbol = data.get("symbol", "Unknown")

                # sector
                if sector not in json_symbols_sector:
                    json_symbols_sector[sector] = []
                json_symbols_sector[sector].append(symbol)
                # industry
                if industry not in json_symbols_industry:
                    json_symbols_industry[industry] = []
                json_symbols_industry[industry].append(symbol)

        with open(json_file_sector, "w", encoding='utf-8') as json_file:
            json.dump({
                "summary": {sector: len(symbols) for sector, symbols in json_symbols_sector.items()},
                "detail": json_symbols_sector
            }, json_file, ensure_ascii=False, indent=4)
        with open(json_file_industry, "w", encoding='utf-8') as json_file:
            json.dump({
                "summary": {sector: len(symbols) for sector, symbols in json_symbols_industry.items()},
                "detail": json_symbols_industry
            }, json_file, ensure_ascii=False, indent=4)

    def analyse_stock_symbols(self) -> List[str]:
        json_file_path = self.config.FOLDER_Watch / "symbols_sector.json"
        with open(json_file_path, "r", encoding='utf-8') as json_file:
            data = json.load(json_file)
            symbols_sector = data.get("detail", {})
            full_symbols = [symbol for symbols in symbols_sector.values() for symbol in symbols]
        return full_symbols
