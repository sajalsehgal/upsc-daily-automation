"""
Scrape daily news from Indian sources for UPSC current affairs
"""
import feedparser
from datetime import datetime
import json
import os

class NewsScraper:
    def __init__(self):
        self.sources = {
            'hindu': 'https://www.thehindu.com/news/national/feeder/default.rss',
            'pib': 'https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1',
            'indian_express': 'https://indianexpress.com/section/india/feed/'
        }
    
    def scrape_rss_feed(self, url, max_articles=10):
        """Get news from RSS feed"""
        try:
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries[:max_articles]:
                articles.append({
                    'title': entry.get('title', ''),
                    'summary': entry.get('summary', entry.get('description', ''))[:500],
                    'link': entry.get('link', ''),
                    'published': entry.get('published', '')
                })
            
            return articles
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return []
    
    def get_daily_news(self):
        """Collect news from all sources"""
        print("\n📰 Scraping news from Indian sources...")
        all_news = []
        
        # The Hindu
        print("  → The Hindu...")
        hindu_articles = self.scrape_rss_feed(self.sources['hindu'], 15)
        all_news.extend(hindu_articles)
        print(f"     Found {len(hindu_articles)} articles")
        
        # PIB (Press Information Bureau)
        print("  → PIB...")
        pib_articles = self.scrape_rss_feed(self.sources['pib'], 10)
        all_news.extend(pib_articles)
        print(f"     Found {len(pib_articles)} articles")
        
        # Indian Express
        print("  → Indian Express...")
        ie_articles = self.scrape_rss_feed(self.sources['indian_express'], 15)
        all_news.extend(ie_articles)
        print(f"     Found {len(ie_articles)} articles")
        
        print(f"\n✅ Total articles scraped: {len(all_news)}")
        return all_news
    
    def save_news(self, news, output_path):
        """Save news to JSON file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'date_hindi': datetime.now().strftime('%d %B %Y'),
            'articles': news,
            'total_articles': len(news)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved to: {output_path}")
        return output_path

def main():
    scraper = NewsScraper()
    news = scraper.get_daily_news()
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    output_path = f'output/upsc/news/daily_news_{date_str}.json'
    
    scraper.save_news(news, output_path)
    
    print(f"\n🎉 News scraping complete!")
    print(f"   Articles: {len(news)}")
    print(f"   File: {output_path}")

if __name__ == "__main__":
    main()
