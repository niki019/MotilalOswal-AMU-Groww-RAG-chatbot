import os
import re
import json
import datetime
import requests
from bs4 import BeautifulSoup

# List of URLs to scrape
URLS = [
    "https://groww.in/mutual-funds/motilal-oswal-large-and-midcap-fund-direct-growth",
    "https://groww.in/mutual-funds/motilal-oswal-most-focused-multicap-35-fund-direct-growth",
    "https://groww.in/mutual-funds/motilal-oswal-active-momentum-fund-direct-growth",
    "https://groww.in/mutual-funds/motilal-oswal-multi-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/motilal-oswal-most-focused-long-term-fund-direct-growth",
    "https://groww.in/mutual-funds/motilal-oswal-contra-fund-direct-growth",
    "https://groww.in/mutual-funds/motilal-oswal-digital-india-fund-direct-growth",
    "https://groww.in/mutual-funds/motilal-oswal-bse-enhanced-value-index-fund-direct-growth",
    "https://groww.in/mutual-funds/motilal-oswal-gold-and-silver-passive-fof-direct-growth",
    "https://groww.in/mutual-funds/motilal-oswal-most-focused-midcap-30-fund-direct-growth",
    "https://groww.in/mutual-funds/motilal-oswal-nifty-500-index-fund-direct-growth",
    "https://groww.in/mutual-funds/motilal-oswal-nifty-500-momentum-50-index-fund-direct-growth",
    "https://groww.in/mutual-funds/motilal-oswal-nifty-capital-market-index-fund-direct-growth",
    "https://groww.in/mutual-funds/motilal-oswal-nifty-india-defence-index-fund-direct-growth",
    "https://groww.in/mutual-funds/motilal-oswal-nifty-midcap-150-index-fund-direct-growth",
    "https://groww.in/mutual-funds/motilal-oswal-small-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/amc/motilal-oswal-mutual-funds"
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Mapping to identify fund tags
FUND_MAPPING = {
    "large_midcap": "large-and-midcap",
    "multicap_35": "most-focused-multicap-35",
    "momentum": "active-momentum",
    "multicap": "multi-cap",
    "long_term": "most-focused-long-term",
    "contra": "contra-fund",
    "digital_india": "digital-india",
    "bse_enhanced_value": "bse-enhanced-value",
    "gold_silver": "gold-and-silver-passive-fof",
    "midcap_30": "most-focused-midcap-30",
    "nifty_500": "nifty-500-index",
    "nifty_500_momentum": "nifty-500-momentum-50",
    "nifty_capital": "nifty-capital-market",
    "nifty_defence": "nifty-india-defence",
    "nifty_midcap": "nifty-midcap-150",
    "small_cap": "small-cap-fund"
}

def clean_html_to_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script, style, noscript, nav, header, footer, svg, and styling tags
    for s in soup(["script", "style", "noscript", "header", "footer", "nav", "form", "iframe", "svg", "path", "g", "defs", "clipPath"]):
        s.decompose()
        
    # Decompose other navigation / user menus
    for s in soup.find_all(class_=re.compile(r"header|footer|nav|sidebar|menu|dropdown|loggedOut", re.I)):
        s.decompose()
        
    # Decompose empty divs and spans that clutter nesting
    for s in soup.find_all(['div', 'span']):
        if not s.get_text(strip=True):
            s.decompose()
        
    lines = []
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'tr', 'span', 'div']):
        # Verify element is still in the tree
        if element.parent is None:
            continue
            
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li']:
            text = element.get_text(separator=" ", strip=True)
            if text and text not in lines and len(text) > 2:
                lines.append(f"{element.name}: {text}")
        elif element.name == 'tr':
            # Format table rows clearly
            cells = [td.get_text(strip=True) for td in element.find_all(['td', 'th'])]
            if cells:
                row_text = " | ".join(cells)
                if row_text not in lines:
                    lines.append(f"Table Row: {row_text}")
        elif element.name in ['div', 'span']:
            # Capture smaller text blocks that contain actual values but no nested structures
            if not element.find(['div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'ul', 'ol']):
                text = element.get_text(strip=True)
                if text and len(text) < 250 and text not in lines and len(text) > 2:
                    # Avoid adding text if it is already a substring of another line
                    if not any(text in existing_line for existing_line in lines):
                        lines.append(text)
                        
    return "\n".join(lines)

def chunk_text(content, url, title, last_updated, fund_tag):
    """
    Implements Heading-Aware Line-by-Line Chunking Strategy.
    """
    chunks = []
    raw_lines = content.split("\n")
    current_chunk = []
    current_size = 0
    
    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
            
        # Flush current chunk on heading triggers
        if (line.startswith("h2:") or line.startswith("h3:")) and current_chunk:
            chunk_text = "\n".join(current_chunk)
            chunks.append({
                "url": url,
                "title": title,
                "content": chunk_text,
                "last_updated": last_updated,
                "fund_tag": fund_tag
            })
            current_chunk = []
            current_size = 0
            
        current_chunk.append(line)
        current_size += len(line)
        
        # Flush on size threshold
        if current_size > 800:
            chunk_text = "\n".join(current_chunk)
            chunks.append({
                "url": url,
                "title": title,
                "content": chunk_text,
                "last_updated": last_updated,
                "fund_tag": fund_tag
            })
            current_chunk = []
            current_size = 0
            
    if current_chunk:
        chunk_text = "\n".join(current_chunk)
        chunks.append({
            "url": url,
            "title": title,
            "content": chunk_text,
            "last_updated": last_updated,
            "fund_tag": fund_tag
        })
        
    return chunks

def run_ingestion():
    print("Starting ingestion script with Heading-Aware Chunking...")
    all_chunks = []
    today_str = datetime.date.today().strftime("%d %b %Y")
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    for url in URLS:
        print(f"Scraping {url}...")
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code == 200:
                html = response.text
                title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.I)
                title = title_match.group(1).strip() if title_match else "Motilal Oswal Scheme"
                
                # Determine fund tag
                fund_tag = "amc"
                for tag, url_part in FUND_MAPPING.items():
                    if url_part in url:
                        fund_tag = tag
                        break
                
                # Clean html to structured text
                clean_text = clean_html_to_text(html)
                
                # Perform chunking immediately at ingestion time
                chunks = chunk_text(clean_text, url, title, today_str, fund_tag)
                all_chunks.extend(chunks)
                print(f"Successfully ingested & chunked {url} into {len(chunks)} chunks.")
            else:
                print(f"Failed to fetch {url}. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            
    # Save pre-computed chunks to JSON
    output_path = os.path.join("data", "chunks.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
        
    print(f"Ingestion completed. Total {len(all_chunks)} chunks saved to {output_path}.")

if __name__ == "__main__":
    run_ingestion()
