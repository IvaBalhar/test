import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tkinter import filedialog, Tk, messagebox
import winsound

def load_urls_and_info_from_excel(file_path):
   return pd.read_excel(file_path).iloc[:, :3]

def download_content(url, max_retries=4):
   headers = {'User-Agent': 'Mozilla/5.0'}
   for _ in range(max_retries):
       try:
           response = requests.get(url, headers=headers)
           response.raise_for_status()
           return response.text
       except requests.RequestException:
           continue
   return None

def extract_text(soup, base_url, processed_texts):
   # Odstranění skriptů, stylů a návratových elementů
   for tag in soup(['script', 'style', 'form', 'nav']):
       tag.decompose()
  
   # Specifické odstranění pro všechny elementy, které obsahují 'header' v ID nebo třídě
   for header in soup.find_all(lambda tag: 'header' in tag.get('id', '') or 'header' in ' '.join(tag.get('class', []))):
       header.decompose()
   for header in soup.find_all(lambda tag: 'footer' in tag.get('id', '') or 'footer' in ' '.join(tag.get('class', []))):
       header.decompose()
   texts = []
   for element in soup.find_all(text=True):
       raw_text = ' '.join(element.split())
       if raw_text and raw_text not in processed_texts:
           processed_texts.add(raw_text)
           if element.parent.name == 'a' and 'href' in element.parent.attrs:
               href = element.parent['href']
               if not href.startswith('#'):
                   full_url = urljoin(base_url, href) if href.startswith('/') else href
                   raw_text += f" ({full_url})"
           texts.append(raw_text)
   return '\n'.join(texts)

def extract_images(soup, base_url):
   images = [urljoin(base_url, img['src']) for img in soup.find_all('img') if img.get('src') and not img['src'].startswith('#')]
   return '\n'.join(images)

def format_entry(product_id, marketplace, url, title, description, text, images):
   return f"{product_id} {marketplace}\n{url}\n\nTitle: {title}\nDescription: {description}\n\n{text}\n\nImages:\n{images}\n" + "-"*50 + "\n\n"

def process_urls(file_path, output_path):
   urls_info = load_urls_and_info_from_excel(file_path)
   max_size = 2000000
   file_index = 0
   current_size = 0
   out_f = open(f"{output_path.rsplit('.', 1)[0]}_{file_index}.{output_path.rsplit('.', 1)[1]}", 'w', encoding='utf-8')
  
   for _, row in urls_info.iterrows():
       product_id, url, marketplace = row
       html_content = download_content(url)
       if html_content:
           soup = BeautifulSoup(html_content, 'html.parser')
           processed_texts = set()
           text = extract_text(soup, url, processed_texts)
           images = extract_images(soup, url)
           title = soup.find("title").get_text(strip=True) if soup.find("title") else "No Title"
           meta_description = soup.find("meta", attrs={"name": "description"})
           description = meta_description['content'] if meta_description and 'content' in meta_description.attrs else "No Description"
           entry = format_entry(product_id, marketplace, url, title, description, text, images)
           if current_size + len(entry) > max_size:
               out_f.close()
               file_index += 1
               out_f = open(f"{output_path.rsplit('.', 1)[0]}_{file_index}.{output_path.rsplit('.', 1)[1]}", 'w', encoding='utf-8')
               current_size = 0
           out_f.write(entry)
           current_size += len(entry)
       else:
           entry = f"{product_id} {marketplace}\n{url}\n\nTak tady se něco nepovedlo...\n\n" + "-"*50 + "\n\n"
           out_f.write(entry)
           current_size += len(entry)

   out_f.close()

def main():
   root = Tk()
   root.withdraw()
   file_path = filedialog.askopenfilename(title="Odkud si mám data nasosat?", filetypes=[("Excel files", "*.xlsx")])
   output_path = filedialog.asksaveasfilename(title="Kam to bude, pane/í?", filetypes=[("Text files", "*.txt")], defaultextension=".txt")
   if file_path and output_path:
       process_urls(file_path, output_path)
       winsound.MessageBeep(winsound.MB_OK)
       messagebox.showinfo("Hotofson", "všechno jsem to postahoval a pročistil")
   else:
       messagebox.showerror("Hej woe!", "Bez vloženého souboru to nepude...")
   root.destroy()

if __name__ == "__main__":
   main()
