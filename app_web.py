import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob

# Load CSV file
df = pd.read_csv("data/apple_income_statements.csv")
df = df.set_index(df.columns[0]).T  # Transpose the table
df.index.name = "Year"
df.reset_index(inplace=True)
# Show column info
st.title("FinQuery - NL Financial Data Analyzer")
st.write("### Available Columns:")
st.write(list(df.columns))

# --- NL Query Input ---
st.subheader("💬 Ask your query in Natural Language")
query = st.text_input("Type your question (e.g. 'Show revenue trend from 2015 to 2021')")

# --- Extract meaning from query ---
if query:
    blob = TextBlob(query.lower())
    nouns = [word for word, pos in blob.tags if pos in ["NN", "NNS", "NNP", "NNPS"]]
    st.write("🧩 Detected keywords:", nouns)

    # Match keywords with columns in CSV
    matched_cols = [col for col in df.columns if any(word in col.lower() for word in nouns)]

    if matched_cols:
        for col in matched_cols:
            st.write(f"📊 Plotting data for: {col}")
            plt.figure(figsize=(10, 4))
            plt.plot(df.columns[1:], df.loc[0, df.columns[1:]], color='lightgray', alpha=0.5)  # dummy trendline
            plt.plot(df.columns[1:], df.loc[df.index[0], df.columns[1:]], marker='o', label=col)
            plt.title(f"{col} Trend Over Time")
            plt.xlabel("Year")
            plt.ylabel(col)
            plt.legend()
            st.pyplot(plt)
    else:
        st.error("❌ Couldn't match your query to any column in the dataset.")
else:
    st.info("Type a financial query above to generate a chart.")

