import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin

st.set_page_config(page_title="Web Scraper and Report Generator")
st.title("🌐 Web Scraper and Report Generator")
st.markdown("Enter a website URL. This tool will extract quote-style content: text, author, tags.")

# Input
url = st.text_input("Enter URL to scrape", "")
max_pages = st.number_input("Max pages to scrape", min_value=1, max_value=100, value=5)

def scrape_quotes_site(base_url, max_pages):
    all_data = []
    current_page = base_url
    page_count = 0

    while current_page and page_count < max_pages:
        try:
            res = requests.get(current_page, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')

            quotes = soup.find_all("div", class_="quote")
            if not quotes:
                break

            for q in quotes:
                text = q.find("span", class_="text").get_text(strip=True) if q.find("span", class_="text") else ""
                author = q.find("small", class_="author").get_text(strip=True) if q.find("small", class_="author") else ""
                tags = [t.get_text(strip=True) for t in q.find_all("a", class_="tag")]

                all_data.append({
                    "URL": current_page,
                    "Title": f"Quote by {author}" if author else "No Author",
                    "Text": text,
                    "Tags": ", ".join(tags)
                })

            next_btn = soup.find("li", class_="next")
            if next_btn and next_btn.find("a"):
                next_link = next_btn.find("a")["href"]
                current_page = urljoin(base_url, next_link)
                page_count += 1
                time.sleep(1)
            else:
                break

        except Exception as e:
            st.warning(f"Error scraping page {current_page}: {e}")
            break

    return pd.DataFrame(all_data)

# Button
if st.button("Start Scraping"):
    if url:
        st.info("Scraping in progress...")
        start_time = time.time()
        df = scrape_quotes_site(url, max_pages)
        duration = round(time.time() - start_time, 2)

        if not df.empty:
            st.success(f"Scraping finished in {duration} seconds. {len(df)} records found.")
            st.dataframe(df)
            st.download_button("📥 Download CSV", df.to_csv(index=False), file_name="report.csv", mime="text/csv")
        else:
            st.warning("No quote data found.")
    else:
        st.error("Please enter a valid URL.")
