import pandas as pd

def csv_to_sentences(csv_path):
    df = pd.read_csv(csv_path)
    sentences = []

    for _, row in df.iterrows():
        sentence = (
            f"On {row['Date']}, store {row['Store ID']} in {row['Region']} sold {row['Units Sold']} units of "
            f"{row['Category']} (Product {row['Product ID']}). Inventory was {row['Inventory Level']}, "
            f"demand forecast was {row['Demand Forecast']}, price was ${row['Price']} with {row['Discount']}% discount. "
            f"Weather was {row['Weather Condition']}, season: {row['Seasonality']}."
        )
        sentences.append(sentence)

    return sentences
