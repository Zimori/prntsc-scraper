import random
import string
import requests
from bs4 import BeautifulSoup

def generate_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

def fetch_prntsc_image(prntsc_id):
    url = f'https://prnt.sc/{prntsc_id}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return None
    soup = BeautifulSoup(resp.text, 'html.parser')
    img = soup.find('img', {'class': 'no-click screenshot-image'})
    if img and img.get('src') and not img['src'].startswith('//st.prntscr.com'):
        return img['src']
    return None

def main(num_links=10):
    found = 0
    for _ in range(num_links):
        prntsc_id = generate_id()
        img_url = fetch_prntsc_image(prntsc_id)
        if img_url:
            print(f'Found: https://prnt.sc/{prntsc_id} -> {img_url}')
            found += 1
        else:
            print(f'No image at: https://prnt.sc/{prntsc_id}')
    print(f'Total found: {found}/{num_links}')

if __name__ == '__main__':
    main(10)
