import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import threading

# Funkce pro stažení obsahu z URL s retry mechanismem a časovým limitem
def download_content_with_timeout(url, timeout=30, max_retries=4):
    headers = {'User-Agent': 'Mozilla/5.0'}
    result = [None]
    
    def download():
        for _ in range(max_retries):
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                result[0] = response.text
                return
            except requests.RequestException:
                continue

    # Spustíme download v jiném vláknu s časovým limitem
    download_thread = threading.Thread(target=download)
    download_thread.start()
    download_thread.join(timeout)  # Čekáme maximálně "timeout" vteřin

    # Pokud se thread dokončil, vrátíme výsledek, jinak None
    return result[0] if download_thread.is_alive() == False else None

# Funkce pro extrakci potenciálních popisů produktu z HTML stránky
def extract_potential_description(soup):
    # Odstraníme běžné elementy, které nechceme
    for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'form']):
        tag.decompose()

    # Získáme všechny textové bloky
    texts = []
    for element in soup.find_all(text=True):
        raw_text = ' '.join(element.split())  # Odstraníme bílé znaky
        # Filtrovat pouze delší texty, které vypadají jako popis produktu
        if len(raw_text) > 50:  # Můžeme upravit tuto hodnotu podle potřeby
            texts.append(raw_text)
    
    # Spojení textových bloků s novými řádky mezi nimi
    return '\n'.join(texts)

# Zpracování CSV souboru a uložení výsledků do nového CSV souboru
def process_first_url(input_csv, output_csv):
    # Načti CSV soubor
    df = pd.read_csv(input_csv)

    # Zpracuje se pouze první řádek
    if len(df) > 0:
        index = 0
        row = df.iloc[0]
        url_1 = row['URL_1']
        url_2 = row['URL_2']
        url_3 = row['URL_3']

        # Zpracování popisu z URL_1 s časovým limitem
        if pd.notna(url_1):
            html_content = download_content_with_timeout(url_1)
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
                df.at[index, 'text1'] = extract_potential_description(soup)
            else:
                df.at[index, 'text1'] = 'chyba'

        # Zpracování popisu z URL_2 s časovým limitem
        if pd.notna(url_2):
            html_content = download_content_with_timeout(url_2)
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
                df.at[index, 'text2'] = extract_potential_description(soup)
            else:
                df.at[index, 'text2'] = 'chyba'

        # Zpracování popisu z URL_3 s časovým limitem
        if pd.notna(url_3):
            html_content = download_content_with_timeout(url_3)
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
                df.at[index, 'text3'] = extract_potential_description(soup)
            else:
                df.at[index, 'text3'] = 'chyba'

        # Výpis průběhu
        print(f"Zpracován první řádek.")

        # Uložení výsledků do nového CSV souboru
        df[['EAN', 'text1', 'text2', 'text3']].head(1).to_csv(output_csv, index=False)
        print(f"Výsledný soubor byl uložen do {output_csv}")

# Hlavní funkce pro spuštění zpracování
def main():
    input_csv = 'products_with_urls.csv'  # Cesta k vstupnímu CSV souboru
    output_csv = 'products_with_texts.csv'  # Cesta k výstupnímu CSV souboru

    process_first_url(input_csv, output_csv)

if __name__ == "__main__":
    main()

