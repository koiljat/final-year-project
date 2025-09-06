import requests
from bs4 import BeautifulSoup
from typing import List, Optional, Tuple, Dict
import time
import logging
import csv
import os
from datetime import datetime
from tqdm import tqdm


log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, "soc_scraper.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file_path), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

BASE_URL = "https://www.comp.nus.edu.sg/features/features-n&pagenum={page_num}"


def get_links_from_page(page_url: str) -> List[str]:
    """Extract all article links from a page."""
    try:
        logger.info(f"Fetching links from page: {page_url}")
        response = requests.get(page_url, timeout=10)
        response.raise_for_status()
        logger.debug(f"Successfully fetched page: {page_url}")
    except requests.RequestException as e:
        logger.error(f"Failed to fetch page {page_url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all(class_="jet-listing-dynamic-link__link")
    extracted_links = list({link.get("href") for link in links if link.get("href")})
    logger.info(f"Found {len(extracted_links)} links on page")
    return extracted_links


def get_content_from_page_html(soup) -> Tuple[str, str]:
    """Extract title and article content from a article page soup."""

    try:
        title_container = soup.find(class_="elementor-widget-container")
        article_title = (
            title_container.get_text(strip=True) if title_container else "No Title"
        )
        logger.debug(f"Extracted title: {article_title[:50]}...")
    except Exception as e:
        article_title = "No Title"
        logger.warning(f"Could not extract article title: {e}")

    try:
        content_container = soup.find(
            "div", class_="elementor-widget-theme-post-content"
        )
        if content_container:
            spans = content_container.find_all("span") or content_container.find_all("p")
            article_content_ls = [span.get_text(strip=True) for span in spans]
            article_content = "\n".join(article_content_ls)
        else:
            article_content = ""
            logger.warning("Could not find content container")
        logger.debug(f"Extracted content length: {len(article_content)} characters")
    except Exception as e:
        article_content = ""
        logger.warning(f"Could not extract article content: {e}")

    return article_title, article_content


def get_author_name_from_page_html(soup) -> str:
    """Extract author name from article page soup."""
    try:
        author_name = (
            soup.find(
                class_="elementor-element elementor-element-dd53caa mt-10 elementor-widget elementor-widget-heading"
            )
            .get_text()
            .strip()
        )
        logger.debug(f"Extracted author: {author_name}")
    except AttributeError:
        author_name = "Unknown"
        logger.warning("Could not extract author name")
    return author_name


def get_date_from_page_html(soup) -> str:
    """Extract published date from article page soup."""
    try:
        date = (
            soup.find(class_="jet-listing jet-listing-dynamic-field display-inline")
            .get_text()
            .strip()
        )
        logger.debug(f"Extracted date: {date}")
    except AttributeError:
        date = "Unknown"
        logger.warning("Could not extract publication date")
    return date


def get_tags_from_page_html(soup) -> List[str]:
    """Extract tags from article page soup."""
    try:
        tags_html = soup.find_all(
            class_="elementor-element elementor-element-ddb1579 tags-list elementor-widget elementor-widget-jet-listing-dynamic-terms"
        )
        tags = [tag.get_text().strip() for tag in tags_html]
        logger.debug(f"Extracted {len(tags)} tags")
    except AttributeError:
        tags = []
        logger.warning("Could not extract tags")
    return tags


def fetch_page_with_retries(
    url: str, retries: int = 3, delay: float = 1.0
) -> requests.Response:
    """Fetch a page with retry logic."""
    for attempt in range(retries):
        try:
            logger.debug(f"Attempt {attempt + 1} to fetch: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            logger.debug(f"Successfully fetched: {url}")
            return response
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < retries - 1:
                time.sleep(delay)

    logger.error(f"Failed to fetch {url} after {retries} attempts")
    return None


def save_to_csv(articles: List[Dict], filename: str = None) -> str:
    """Save articles to CSV file in data/soc directory."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "soc")
    os.makedirs(data_dir, exist_ok=True)

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scraped_articles_{timestamp}.csv"

    filepath = os.path.join(data_dir, filename)

    try:
        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            if not articles:
                logger.warning("No articles to save")
                return filepath

            fieldnames = ["title", "content", "author", "date", "tags", "url"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for article in articles:

                article_copy = article.copy()
                article_copy["tags"] = (
                    "; ".join(article["tags"]) if article["tags"] else ""
                )
                writer.writerow(article_copy)

        logger.info(f"Successfully saved {len(articles)} articles to {filepath}")
        return filepath

    except Exception as e:
        logger.error(f"Failed to save CSV file: {e}")
        raise


def scrape_feature_articles(max_pages: Optional[int] = None) -> List[Dict]:
    """Scrape all articles up to max_pages and return a list of article dicts.
    If max_pages is None, scrape all available pages until no more articles are found.
    """

    if max_pages is None:
        logger.info("Starting scraper for all available pages")
        scrape_all_pages = True
    else:
        logger.info(f"Starting scraper for up to {max_pages} pages")
        scrape_all_pages = False

    all_articles = []
    seen_urls = set()
    total_articles_scraped = 0
    total_duplicates_skipped = 0
    page_num = 1

    print("🔍 Discovering articles...")
    all_links = []
    temp_seen = set()

    with tqdm(desc="Discovering pages", unit="page") as page_pbar:
        while True:
            if not scrape_all_pages and page_num > max_pages:
                break

            page_url = BASE_URL.format(page_num=page_num)
            links = get_links_from_page(page_url)

            if not links:
                break

            unique_page_links = [link for link in links if link not in temp_seen]
            all_links.extend(unique_page_links)
            temp_seen.update(unique_page_links)

            page_pbar.set_postfix(
                {"articles_found": len(all_links), "current_page": page_num}
            )
            page_pbar.update(1)
            page_num += 1

    if not all_links:
        logger.warning("No articles found")
        return []

    print(f"\n📚 Found {len(all_links)} unique articles to scrape")

    with tqdm(
        total=len(all_links),
        desc="Scraping articles",
        unit="article",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
    ) as pbar:

        for i, link in enumerate(all_links):

            pbar.set_postfix(
                {"success": total_articles_scraped, "skipped": total_duplicates_skipped}
            )

            response = fetch_page_with_retries(link)
            if response is None:
                logger.error(f"Skipping article due to fetch failure: {link}")
                total_duplicates_skipped += 1
                pbar.update(1)
                continue

            try:
                soup = BeautifulSoup(response.text, "html.parser")
                title, content = get_content_from_page_html(soup)
                author = get_author_name_from_page_html(soup)
                date = get_date_from_page_html(soup)
                tags = get_tags_from_page_html(soup)

                article = {
                    "title": title,
                    "content": content,
                    "author": author,
                    "date": date,
                    "tags": tags,
                    "url": link,
                }

                all_articles.append(article)
                total_articles_scraped += 1

                pbar.set_description(f"✅ {title[:30]}..." if title else "✅ Untitled")

            except Exception as e:
                logger.error(f"Error processing article {link}: {e}")
                total_duplicates_skipped += 1

            pbar.update(1)
            time.sleep(0.5)

    print(f"\n🎉 Scraping completed!")
    print(f"📊 Total articles scraped: {total_articles_scraped}")
    if total_duplicates_skipped > 0:
        print(f"⚠️  Total articles skipped: {total_duplicates_skipped}")

    return all_articles


def main():
    """Main function to run the scraper."""
    start_time = time.time()
    try:
        print("🚀 Starting NUS School of Computing feature articles scraper")
        articles = scrape_feature_articles()

        if articles:
            print("\n💾 Saving to CSV...")
            with tqdm(desc="Saving", total=1) as save_pbar:
                csv_filepath = save_to_csv(articles)
                save_pbar.update(1)

            print(f"✅ Scraping completed successfully!")
            print(f"📄 CSV file saved at: {csv_filepath}")
        else:
            print("⚠️  No articles were scraped")

    except Exception as e:
        logger.error(f"❌ Scraper failed with error: {e}")
        raise
    finally:
        elapsed = time.time() - start_time
        print(f"⏱️ Total time taken: {elapsed:.2f} seconds")


if __name__ == "__main__":
    main()
