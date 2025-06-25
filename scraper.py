import random
import string
import requests
from bs4 import BeautifulSoup
import os
import datetime
from PIL import Image
from io import BytesIO

def generate_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

def fetch_prntsc_image(prntsc_id, save_folder=None):
    url = f'https://prnt.sc/{prntsc_id}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return None
    soup = BeautifulSoup(resp.text, 'html.parser')
    img = soup.find('img', {'class': 'no-click screenshot-image'})
    if img and img.get('src') and not img['src'].startswith('//st.prntscr.com'):
        img_url = img['src']
        if save_folder:
            try:
                img_resp = requests.get(img_url, headers=headers)
                if img_resp.status_code != 200:
                    return None
                if not img_resp.headers.get('Content-Type', '').startswith('image/'):
                    return None
                # Try to open with PIL to ensure it's a valid image
                try:
                    Image.open(BytesIO(img_resp.content)).verify()
                except Exception:
                    return None
                ext = os.path.splitext(img_url)[1].split('?')[0] or '.jpg'
                filename = f'{prntsc_id}{ext}'
                with open(os.path.join(save_folder, filename), 'wb') as f:
                    f.write(img_resp.content)
            except Exception as e:
                print(f'Error saving {img_url}: {e}')
        return img_url
    return None

def main(num_links=10, save_folder=None):
    found = 0
    now = datetime.datetime.now()
    subfolder = f"img-{now.strftime('%Y%m%d-%H%M%S')}"
    if save_folder:
        save_folder = os.path.join(save_folder, subfolder)
        os.makedirs(save_folder, exist_ok=True)
    attempts = 0
    while found < num_links:
        prntsc_id = generate_id()
        img_url = fetch_prntsc_image(prntsc_id, save_folder=save_folder)
        attempts += 1
        if img_url:
            print(f'Found: https://prnt.sc/{prntsc_id} -> {img_url}')
            found += 1
        else:
            print(f'No image at: https://prnt.sc/{prntsc_id}')
    print(f'Total found: {found}/{attempts} (requested: {num_links})')

if __name__ == '__main__':
    main(10, save_folder='images')
