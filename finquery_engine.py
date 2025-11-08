import pandas as pd

class FinQueryEngine:
    def __init__(self, csv_path="data/apple_income_statements.csv"):
        try:
            # Load CSV (no header issue)
            df = pd.read_csv(csv_path)

            # Transpose the dataset so that years become rows
            df = df.set_index(df.columns[0]).T.reset_index()
            df.rename(columns={'index': 'Year'}, inplace=True)

            # Convert all numeric columns
            for col in df.columns[1:]:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            self.df = df
            print("✅ Data loaded and transformed successfully!")
            print("Columns available:", list(self.df.columns))
            print("\nData Preview:")
            print(self.df.head())

        except Exception as e:
            print("❌ Error loading CSV:", e)

    def _find_col(self, keyword):
        """Find the first column containing a keyword (case-insensitive)"""
        for col in self.df.columns:
            if keyword.lower() in col.lower():
                return col
        return None

    def query(self, q: str):
        q = q.lower()

        # --- Revenue Queries ---
        if "revenue" in q:
            col = self._find_col("revenue")
            if not col:
                return "❌ No column related to 'Revenue' found."

            if "growth" in q:
                df = self.df[["Year", col]].copy()
                df["Revenue Growth (%)"] = df[col].pct_change() * 100
                return df

            return self.df[["Year", col]]

        # --- Income Queries ---
        elif "income" in q:
            col = self._find_col("income")
            if not col:
                return "❌ No column related to 'Income' found."
            return self.df[["Year", col]]

        # --- Assets Queries ---
        elif "asset" in q:
            col = self._find_col("asset")
            if not col:
                return "❌ No column related to 'Assets' found."
            return self.df[["Year", col]]

        # --- Liabilities Queries ---
        elif "liabilit" in q:
            col = self._find_col("liabilit")
            if not col:
                return "❌ No column related to 'Liabilities' found."
            return self.df[["Year", col]]

        # --- Cash Queries ---
        elif "cash" in q:
            col = self._find_col("cash")
            if not col:
                return "❌ No column related to 'Cash' found."
            return self.df[["Year", col]]

        else:
            return "❌ Sorry, I couldn’t understand that query."




