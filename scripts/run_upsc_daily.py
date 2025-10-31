"""
Complete daily automation for UPSC Current Affairs
Run this once per day (ideally at 6 AM IST)
"""
from datetime import datetime
import os
import sys

# Import our modules
from scrape_news import NewsScraper
from generate_upsc_script import UPSCScriptGenerator
from create_upsc_video import UPSCVideoCreator

def main():
    print("\n" + "="*70)
    print("  UPSC DAILY CURRENT AFFAIRS - AUTOMATED PIPELINE")
    print("="*70)
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    print(f"\nDate: {date_str}")
    
    # STEP 1: Scrape News
    print("\n" + "="*70)
    print("  STEP 1: Scraping News")
    print("="*70)
    
    scraper = NewsScraper()
    news = scraper.get_daily_news()
    news_file = f'output/upsc/news/daily_news_{date_str}.json'
    scraper.save_news(news, news_file)
    
    # STEP 2: Generate Script
    print("\n" + "="*70)
    print("  STEP 2: Generating Hindi Script")
    print("="*70)
    
    generator = UPSCScriptGenerator()
    news_data = generator.load_news(news_file)
    script = generator.generate_hindi_script(news_data)
    script_file = f'output/upsc/scripts/script_{date_str}.txt'
    generator.save_script(script, script_file)
    
    # STEP 3: Create Video
    print("\n" + "="*70)
    print("  STEP 3: Creating Video")
    print("="*70)
    
    creator = UPSCVideoCreator()
    result = creator.create_complete_video(script_file, date_str)
    
    # Summary
    print("\n" + "="*70)
    print("  DAILY AUTOMATION COMPLETE!")
    print("="*70)
    print(f"\nVideo: {result['video']}")
    print(f"Thumbnail: {result['thumbnail']}")
    print(f"\nNext: Upload to YouTube")
    print("="*70)
    
    return result

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
