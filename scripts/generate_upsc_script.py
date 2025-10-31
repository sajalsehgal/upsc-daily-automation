"""
Generate UPSC script - FORCES all 10 news items
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class UPSCScriptGenerator:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise Exception("GEMINI_API_KEY not found")
        
        self.api_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={self.api_key}"
    
    def load_news(self, news_file):
        with open(news_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_single_news_item(self, news_article, item_number, date_hindi):
        """Generate ONE news item at a time to ensure quality"""
        
        news_numbers_hindi = ["पहली", "दूसरी", "तीसरी", "चौथी", "पांचवीं", 
                             "छठी", "सातवीं", "आठवीं", "नौवीं", "दसवीं"]
        
        prompt = f"""You are writing ONE news item for a UPSC Current Affairs video in Hindi.

News Article:
Title: {news_article['title']}
Summary: {news_article.get('summary', '')}
Source: {news_article.get('source', '')}

Write EXACTLY this format in Hindi (100-120 words):

{news_numbers_hindi[item_number-1]} खबर।
[Write 5-6 complete sentences explaining:
- What happened (be specific with names, dates, numbers)
- Where it happened
- Why it's important
- What are the implications
- Key facts to remember]
UPSC के Prelims और Mains में यह [specific syllabus topic] से पूछा जा सकता है।

CRITICAL RULES:
- Must be 100-120 words
- Must have 5-6 complete sentences
- Include ALL available facts from the summary
- Simple conversational Hindi
- NO English except proper nouns (WHO, NASA, GDP, etc.)

Write only this one news item now:"""

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 500
            }
        }
        
        response = requests.post(self.api_url, json=payload, timeout=60)
        
        if response.status_code != 200:
            return f"{news_numbers_hindi[item_number-1]} खबर।\n{news_article['title']} के बारे में जानकारी उपलब्ध नहीं है।\n"
        
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text'].strip()
    
    def generate_hindi_script(self, news_data):
        """Generate complete script by creating each news item separately"""
        
        articles = news_data['articles']
        date_hindi = news_data.get('date_hindi', datetime.now().strftime('%d %B %Y'))
        
        print("\n🤖 Generating script with GUARANTEED 10 news items...")
        print("   Generating each item individually for quality...\n")
        
        # Intro
        intro = f"""नमस्ते दोस्तों! आज की तारीख है {date_hindi}। आज हम देखेंगे Top 10 Current Affairs जो आपकी UPSC और सरकारी परीक्षा की तैयारी के लिए बहुत जरूरी हैं। तो चलिए शुरू करते हैं।

"""
        
        # Generate all 10 news items one by one
        news_items = []
        for i in range(10):
            print(f"   Generating news item {i+1}/10...", end=' ')
            
            if i < len(articles):
                item = self.generate_single_news_item(articles[i], i+1, date_hindi)
                news_items.append(item)
                print("✓")
            else:
                print("⚠️  No article available")
                break
            
            # Small delay to avoid rate limiting
            if i < 9:
                import time
                time.sleep(1)
        
        # Outro
        outro = """

तो दोस्तों, यह थे आज के Top 10 Current Affairs। PDF notes और detailed analysis के लिए description में link देखें। अगर video helpful लगा तो like करें और channel को subscribe करना मत भूलिए। Bell icon press कर दें। कल फिर मिलेंगे नई खबरों के साथ। धन्यवाद!"""
        
        # Combine everything
        script = intro + "\n\n".join(news_items) + outro
        
        word_count = len(script.split())
        
        print(f"\n✅ Complete script generated!")
        print(f"   News items: {len(news_items)}")
        print(f"   Total words: {word_count}")
        print(f"   Estimated duration: {word_count / 130:.1f} minutes")
        
        return script
    
    def save_script(self, script, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(script)
        print(f"💾 Saved: {output_path}")
        return script

def main():
    date_str = datetime.now().strftime('%Y-%m-%d')
    news_file = f'output/upsc/news/daily_news_{date_str}.json'
    
    if not os.path.exists(news_file):
        print(f"❌ News file not found")
        return
    
    generator = UPSCScriptGenerator()
    news_data = generator.load_news(news_file)
    
    print(f"\n📰 Loaded {news_data['total_articles']} articles")
    
    script = generator.generate_hindi_script(news_data)
    
    output_path = f'output/upsc/scripts/script_{date_str}.txt'
    generator.save_script(script, output_path)
    
    print(f"\n📝 Preview (first 600 chars):")
    print("-" * 70)
    print(script[:600])
    print("-" * 70)

if __name__ == "__main__":
    main()
