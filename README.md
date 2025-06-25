# prnt.sc Image Scraper

A robust Python tool to scrape and download images from prnt.sc (Lightshot) using random 6-character IDs. Images are saved in timestamped subfolders for easy organization. The script ensures only valid, loadable images are saved.

## Features

- Generates random prnt.sc IDs and fetches images.
- Saves images in `images/img-YYYYMMDD-HHMMSS/` subfolders.
- Skips broken, placeholder, or invalid images using HTTP, Content-Type, and Pillow validation.
- Keeps searching until the requested number of valid images are found.
- Clean project structure with images excluded from git.
- Easily extensible for new features (see below).

## Requirements

- Python 3.7+
- `requests`
- `beautifulsoup4`
- `pillow`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the scraper (default: find 10 images):

```bash
python3 scraper.py
```

You can customize the number of images and output folder by editing the `main()` call at the bottom of `scraper.py`:

```python
if __name__ == '__main__':
    main(20, save_folder='images')  # Example: find 20 images
```

## How It Works

1. **ID Generation:** Random 6-character alphanumeric IDs are generated to form prnt.sc URLs.
2. **Fetching:** Each URL is fetched with a browser-like User-Agent.
3. **Parsing:** The image URL is extracted from the HTML using BeautifulSoup.
4. **Validation:**
   - The image is only saved if:
     - The HTTP response is 200.
     - The Content-Type is an image.
     - The image can be opened by Pillow (not broken or placeholder).
5. **Saving:**
   - Images are saved in a subfolder named `img-YYYYMMDD-HHMMSS` under `images/`.
   - The script continues until the requested number of valid images are found.

## Extending the Scraper

You can easily add new features:

- **Command-line arguments:** Use `argparse` to allow users to specify the number of images, output folder, or ID pattern.
- **Sequential ID search:** Instead of random, try sequential or custom ID lists.
- **Image viewer:** Add a GUI (e.g., with Tkinter or Pillow) to preview images after download.
- **Logging:** Save results and errors to a log file or CSV.
- **Concurrency:** Use `concurrent.futures` or `asyncio` to speed up scraping (be mindful of rate limits).
- **Proxy support:** Add proxy rotation to avoid rate limiting.
- **Captcha detection:** Detect and handle captchas or blocks.

## Project Structure

```bash

prntsc-scraper/
├── images/                  # Downloaded images (gitignored)
│   └── img-YYYYMMDD-HHMMSS/ # Timestamped subfolders
├── scraper.py               # Main script
├── requirements.txt         # Python dependencies
├── .gitignore               # Excludes images/
└── README.md                # This file
```

## License

MIT License

---

**Contributions and suggestions are welcome!**
