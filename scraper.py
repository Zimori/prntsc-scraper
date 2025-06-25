import random
import string
import requests
from bs4 import BeautifulSoup
import os
import datetime
from PIL import Image
from io import BytesIO
import argparse
from tqdm import tqdm
import pytesseract
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def process_image(prntsc_id, search_texts, save_folder):
    img_url = fetch_prntsc_image(prntsc_id, save_folder=None)
    if not img_url:
        return False, prntsc_id, None, None, None
    try:
        img_resp = requests.get(img_url, headers={'User-Agent': 'Mozilla/5.0'})
        if img_resp.status_code == 200 and img_resp.headers.get('Content-Type', '').startswith('image/'):
            img = Image.open(BytesIO(img_resp.content))
            if search_texts:
                text = pytesseract.image_to_string(img)
                if any(s.lower() in text.lower() for s in search_texts):
                    ext = os.path.splitext(img_url)[1].split('?')[0] or '.jpg'
                    filename = f'{prntsc_id}{ext}'
                    with open(os.path.join(save_folder, filename), 'wb') as f:
                        f.write(img_resp.content)
                    return True, prntsc_id, img_url, '[MATCH]', None
                else:
                    return False, prntsc_id, img_url, None, 'string_not_found'
            else:
                ext = os.path.splitext(img_url)[1].split('?')[0] or '.jpg'
                filename = f'{prntsc_id}{ext}'
                with open(os.path.join(save_folder, filename), 'wb') as f:
                    f.write(img_resp.content)
                return True, prntsc_id, img_url, None, None
        else:
            return False, prntsc_id, None, None, None
    except Exception as e:
        print(f'Error processing {img_url}: {e}')
        return False, prntsc_id, img_url, None, None

def run_scraper(num_links=10, search_text=None, workers=8):
    found = 0
    failed = 0
    not_found_string = 0
    now = datetime.datetime.now()
    save_folder = os.path.join('images', f"img-{now.strftime('%Y%m%d-%H%M%S')}")
    os.makedirs(save_folder, exist_ok=True)
    attempts = 0
    from tqdm import tqdm
    # Prepare search_texts as a list
    search_texts = [s.strip() for s in search_text.split(',')] if search_text else None
    with ThreadPoolExecutor(max_workers=workers) as executor, tqdm(total=num_links, desc='Downloading images') as pbar:
        futures = set()
        while found < num_links:
            # Launch new tasks if needed
            while len(futures) < workers and found + len(futures) < num_links:
                prntsc_id = generate_id()
                futures.add(executor.submit(process_image, prntsc_id, search_texts, save_folder))
            # Wait for any to complete
            done, futures = set(), futures
            for future in as_completed(futures):
                success, prntsc_id, img_url, match, reason = future.result()
                attempts += 1
                if success:
                    found += 1
                    pbar.update(1)
                    if match:
                        print(f'{match} Found and saved: https://prnt.sc/{prntsc_id} -> {img_url}')
                    else:
                        print(f'Found: https://prnt.sc/{prntsc_id} -> {img_url}')
                elif reason == 'string_not_found':
                    print(f"Image found, but none of the strings {search_texts} present: https://prnt.sc/{prntsc_id}")
                    not_found_string += 1
                else:
                    print(f'No image at: https://prnt.sc/{prntsc_id}')
                    failed += 1
                futures.remove(future)
                break  # Only process one completed future at a time
    fail_percent = (failed / (found + failed + not_found_string)) * 100 if (found + failed + not_found_string) > 0 else 0
    print(f'Total found: {found}/{attempts} (requested: {num_links})')
    print(f'Failed: {failed} ({fail_percent:.2f}% of attempts)')
    if search_text:
        print(f"Images found but without any of the strings {search_texts}: {not_found_string}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='prnt.sc image scraper')
    default_num_images = 10
    parser.add_argument('-n', '--num-images', type=int, default=None, help=f'Number of valid images to download (default: {default_num_images})')
    parser.add_argument('-s', '--search', type=str, default=None, help='Text to search for in images (OCR)')
    parser.add_argument('-w', '--workers', type=int, default=8, help='Number of concurrent workers (default: 8)')
    args = parser.parse_args()
    if args.num_images is None:
        print(f'No image number requested, using default value {default_num_images}...')
        num_images = default_num_images
    else:
        num_images = args.num_images
    run_scraper(num_links=num_images, search_text=args.search, workers=args.workers)
