"""
Fetch UPSC-RELEVANT Current Affairs from proper sources
"""
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

class UPSCNewsCollector:
    def __init__(self):
        # UPSC-focused RSS feeds
        self.feeds = {
            # Government/Policy
            'pib': 'https://pib.gov.in/RSS/RssFeed.aspx',
            
            # UPSC Current Affairs Sites
            'drishti_ias': 'https://www.drishtiias.com/feed',
            'vision_ias': 'https://www.visionias.in/feed',
            
            # Serious News (UPSC relevant)
            'hindu_national': 'https://www.thehindu.com/news/national/feeder/default.rss',
            'hindu_international': 'https://www.thehindu.com/news/international/feeder/default.rss',
            'hindu_business': 'https://www.thehindu.com/business/feeder/default.rss',
            'hindu_science': 'https://www.thehindu.com/sci-tech/science/feeder/default.rss',
            'indian_express_india': 'https://indianexpress.com/section/india/feed/',
            'indian_express_world': 'https://indianexpress.com/section/world/feed/',
            
            # Economy
            'livemint': 'https://www.livemint.com/rss/economy',
            'economic_times': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
            
            # Environment/Science
            'down_to_earth': 'https://www.downtoearth.org.in/rss',
            
            # International Relations
            'mea_india': 'https://mea.gov.in/rssfeed.xml'
        }
        
        # UPSC-relevant keywords
        self.upsc_keywords = [
            # Government/Polity
            'supreme court', 'parliament', 'lok sabha', 'rajya sabha', 'bill', 'amendment',
            'president', 'prime minister', 'chief minister', 'governor', 'cabinet', 'ministry',
            'election', 'electoral', 'constitution', 'article', 'act', 'law', 'judiciary',
            
            # Economy
            'gdp', 'inflation', 'budget', 'fiscal', 'monetary', 'reserve bank', 'rbi',
            'world bank', 'imf', 'trade', 'export', 'import', 'gst', 'tax', 'subsidy',
            'disinvestment', 'privatization', 'fdi', 'stock market', 'sensex', 'nifty',
            
            # International Relations
            'india', 'pakistan', 'china', 'usa', 'russia', 'treaty', 'agreement', 'summit',
            'united nations', 'brics', 'g20', 'asean', 'saarc', 'nato', 'bilateral',
            'foreign policy', 'diplomatic', 'ambassador',
            
            # Science & Technology
            'isro', 'drdo', 'chandrayaan', 'gaganyaan', 'satellite', 'mission', 'space',
            'artificial intelligence', 'quantum', 'semiconductor', 'technology', 'research',
            'vaccine', 'covid', 'health', 'pandemic',
            
            # Environment
            'climate change', 'global warming', 'paris agreement', 'cop', 'pollution',
            'wildlife', 'forest', 'biodiversity', 'conservation', 'renewable energy',
            'solar', 'wind energy', 'electric vehicle',
            
            # Geography/Disasters
            'earthquake', 'cyclone', 'flood', 'drought', 'tsunami', 'landslide',
            
            # Awards/Achievements
            'nobel prize', 'bharat ratna', 'padma', 'award', 'medal', 'olympic',
            
            # Schemes/Initiatives
            'scheme', 'yojana', 'mission', 'programme', 'initiative', 'policy',
            'swachh bharat', 'ayushman', 'ujjwala', 'pmay', 'mudra'
        ]
    
    def is_upsc_relevant(self, title, summary):
        """Check if article is UPSC relevant"""
        text = (title + " " + summary).lower()
        
        # Skip entertainment/sports (unless major)
        skip_keywords = ['cricket', 'bollywood', 'film', 'actor', 'actress', 'movie', 
                        'celebrity', 'ipl', 'football match', 'tennis match']
        
        if any(word in text for word in skip_keywords):
            return False
        
        # Must contain UPSC keywords
        return any(keyword in text for keyword in self.upsc_keywords)
    
    def fetch_all_news(self):
        """Fetch news from all sources"""
        
        print("\n📰 Fetching UPSC-relevant current affairs...")
        
        all_articles = []
        
        for source_name, feed_url in self.feeds.items():
            try:
                print(f"   {source_name}...", end=' ')
                
                feed = feedparser.parse(feed_url)
                
                count = 0
                for entry in feed.entries[:20]:  # Check first 20
                    title = entry.get('title', '')
                    summary = entry.get('summary', entry.get('description', ''))
                    link = entry.get('link', '')
                    
                    # Clean HTML from summary
                    if summary:
                        soup = BeautifulSoup(summary, 'html.parser')
                        summary = soup.get_text()
                    
                    # Check if UPSC relevant
                    if self.is_upsc_relevant(title, summary):
                        all_articles.append({
                            'title': title,
                            'summary': summary[:500],
                            'link': link,
                            'source': source_name,
                            'published': entry.get('published', '')
                        })
                        count += 1
                
                print(f"✓ ({count} relevant)")
                
            except Exception as e:
                print(f"✗ ({e})")
        
        # Remove duplicates by title similarity
        unique_articles = []
        seen_titles = set()
        
        for article in all_articles:
            title_key = article['title'].lower()[:50]  # First 50 chars
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)
        
        print(f"\n✅ Found {len(unique_articles)} UPSC-relevant articles")
        
        # Sort by relevance (prioritize government sources)
        priority_sources = ['pib', 'drishti_ias', 'vision_ias', 'mea_india']
        
        unique_articles.sort(key=lambda x: (
            0 if x['source'] in priority_sources else 1,
            -len(x['summary'])  # Longer summaries = more detail
        ))
        
        return unique_articles[:15]  # Return top 15
    
    def save_news(self, articles):
        """Save to JSON"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        date_hindi = datetime.now().strftime('%d %B %Y')
        
        data = {
            'date': date_str,
            'date_hindi': date_hindi,
            'total_articles': len(articles),
            'articles': articles
        }
        
        os.makedirs('output/upsc/news', exist_ok=True)
        output_file = f'output/upsc/news/daily_news_{date_str}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved: {output_file}")
        
        return output_file

def main():
    collector = UPSCNewsCollector()
    articles = collector.fetch_all_news()
    
    if articles:
        collector.save_news(articles)
        
        print("\n📋 Sample articles:")
        for i, article in enumerate(articles[:5], 1):
            print(f"\n{i}. {article['title']}")
            print(f"   Source: {article['source']}")
            print(f"   Summary: {article['summary'][:100]}...")
    else:
        print("❌ No articles found")

if __name__ == "__main__":
    main()
