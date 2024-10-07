import pandas as pd
from googlesearch import search

# Načti CSV soubor
df = pd.read_csv('Products.csv')

# Přidej nové sloupce pro URL (pro každý řádek)
df['URL_1'] = ''
df['URL_2'] = ''
df['URL_3'] = ''

# Pro každý řádek proveď vyhledávání
for index, row in df.iterrows():
    identifier = row['EAN']  # Použij správný název sloupce s identifikátorem (EAN)
    query = str(identifier) + " česky"  # Přidání řetězce "česky" k EAN

    # Získání URL pomocí vyhledávání, omezíme na 3 URL
    urls = []
    for url in search(query):  # Provádíme vyhledávání pro každý řádek
        urls.append(url)
        if len(urls) >= 3:
            break  # Omezíme na prvních 3 výsledky

    # Uložení URL do příslušných sloupců pro daný řádek
    if len(urls) > 0:
        df.at[index, 'URL_1'] = urls[0]
    if len(urls) > 1:
        df.at[index, 'URL_2'] = urls[1]
    if len(urls) > 2:
        df.at[index, 'URL_3'] = urls[2]

    # Výpis průběhu zpracování řádku (volitelné)
    print(f"Zpracován řádek {index + 1}/{len(df)}")

# Ulož výsledky zpět do CSV, když jsou všechny řádky zpracovány
df.to_csv('products_with_urls.csv', index=False)

print("Všechny řádky byly zpracovány a uloženy do products_with_urls.csv")
