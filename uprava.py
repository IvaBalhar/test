import pandas as pd

# Načti stávající CSV soubor
df = pd.read_csv('Products.csv')

# Přejmenuj sloupce
df.columns = ['EAN', 'URL1', 'URL2', 'URL3']

# Ulož upravený CSV soubor
df.to_csv('Products.csv', index=False)

print("Názvy sloupců byly úspěšně upraveny.")
