# Web Scraper: Multi-Level Data Extraction

## Overview
This Python script performs recursive web scraping based on a given query. It collects various types of data from the top X search results and their sub-links, including:

- **Text Content** (with summarization)
- **Images**
- **Videos**
- **Links**
- **Emails**
- **Phone Numbers**
- **Documents** (PDF, DOCX, etc.)

All extracted data is stored in an SQLite database for easy access and further processing.

## Features
- Recursively scrapes data from web pages and their sub-links
- Extracts structured information (text, images, emails, etc.)
- Saves data in an SQLite database
- Summarizes scraped text content
- Downloads found documents

## Requirements
Make sure you have the following dependencies installed:

```bash
pip install requests beautifulsoup4 selenium sqlite3 pandas etc
```

Additionally, you'll need a **SerpAPI** key to perform Google searches. Sign up at [SerpAPI](https://serpapi.com/) and insert your API key in the script.

## Setup
1. Clone the repository:

3. Add your **SerpAPI** key in the script:
   ```python
   SERPAPI_KEY = "your_serpapi_key_here"
   ```

## Usage
Run the script with a query to start scraping:

```bash
python scraper.py
```
Enter your search query when prompted.

### Accessing the Data
The script saves extracted data into an SQLite database (`scraper_database.db`). You can view the data using an online SQLite viewer, such as:
[https://sqliteviewer.app/#/scraper_database.db/table/link_details/](https://sqliteviewer.app/#/scraper_database.db/table/link_details/)

## Notes
- Be mindful of sending too many requests to search engines, as it may trigger CAPTCHA challenges.
- For large-scale scraping, consider implementing **rate-limiting** and **proxy rotation** to avoid getting blocked.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contributions
Feel free to fork this repository and contribute! Pull requests are welcome.



