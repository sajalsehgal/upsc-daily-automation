"""
Generate UPSC script - with proper error handling
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
        """Generate ONE news item with error handling"""
        
        news_numbers_hindi = ["पहली", "दूसरी", "तीसरी", "चौथी", "पांचवीं", 
                             "छठी", "सातवीं", "आठवीं", "नौवीं", "दसवीं"]
        
        prompt = f"""You are writing ONE news item for a UPSC Current Affairs video in Hindi.

News Article:
Title: {news_article['title']}
Summary: {news_article.get('summary', '')}

Write EXACTLY in this format (100-120 words):

{news_numbers_hindi[item_number-1]} खबर।
[Write 5-6 complete sentences explaining what happened, where, why it's important, and key facts to remember]
UPSC के Prelims और Mains में यह [specific topic] से पूछा जा सकता है।

Use simple conversational Hindi. Include specific details.

Write only this one news item:"""

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 500
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=60)
            
            if response.status_code != 200:
                print(f"\n   ❌ API Error {response.status_code}: {response.text}")
                return f"{news_numbers_hindi[item_number-1]} खबर।\n{news_article['title']} के बारे में जानकारी संकलित की जा रही है।\n"
            
            result = response.json()
            
            # Check for errors in response
            if 'candidates' not in result:
                print(f"\n   ❌ No candidates in response: {result}")
                return f"{news_numbers_hindi[item_number-1]} खबर।\n{news_article['title']}।\n"
            
            if not result['candidates']:
                print(f"\n   ❌ Empty candidates")
                return f"{news_numbers_hindi[item_number-1]} खबर।\n{news_article['title']}।\n"
            
            candidate = result['candidates'][0]
            
            if 'content' not in candidate:
                print(f"\n   ❌ No content in candidate: {candidate}")
                return f"{news_numbers_hindi[item_number-1]} खबर।\n{news_article['title']}।\n"
            
            if 'parts' not in candidate['content']:
                print(f"\n   ❌ No parts in content: {candidate['content']}")
                return f"{news_numbers_hindi[item_number-1]} खबर।\n{news_article['title']}।\n"
            
            text = candidate['content']['parts'][0]['text'].strip()
            return text
            
        except Exception as e:
            print(f"\n   ❌ Exception: {e}")
            return f"{news_numbers_hindi[item_number-1]} खबर।\n{news_article['title']} पर विस्तृत जानकारी जल्द उपलब्ध होगी।\n"
    
    def generate_hindi_script(self, news_data):
        """Generate complete script"""
        
        articles = news_data['articles']
        date_hindi = news_data.get('date_hindi', datetime.now().strftime('%d %B %Y'))
        
        print("\n🤖 Generating script with GUARANTEED 10 news items...")
        print("   Generating each item individually...\n")
        
        # Intro
        intro = f"""नमस्ते दोस्तों! आज की तारीख है {date_hindi}। आज हम देखेंगे Top 10 Current Affairs जो आपकी UPSC और सरकारी परीक्षा की तैयारी के लिए बहुत जरूरी हैं। तो चलिए शुरू करते हैं।

"""
        
        # Generate 10 news items
        news_items = []
        for i in range(10):
            print(f"   Generating news item {i+1}/10...", end=' ')
            
            if i < len(articles):
                item = self.generate_single_news_item(articles[i], i+1, date_hindi)
                news_items.append(item)
                print("✓")
            else:
                print("⚠️  No article")
                break
            
            # Delay between requests
            if i < 9:
                import time
                time.sleep(2)
        
        # Outro
        outro = """

तो दोस्तों, यह थे आज के Top 10 Current Affairs। PDF notes के लिए description में link देखें। Video पसंद आया तो like और subscribe करें। Bell icon press कर दें। कल फिर मिलेंगे। धन्यवाद!"""
        
        # Combine
        script = intro + "\n\n".join(news_items) + outro
        
        word_count = len(script.split())
        
        print(f"\n✅ Script generated!")
        print(f"   News items: {len(news_items)}")
        print(f"   Words: {word_count}")
        print(f"   Est. duration: {word_count / 130:.1f} minutes")
        
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
    
    print(f"\n📝 Preview:")
    print("-" * 70)
    print(script[:600])
    print("-" * 70)

if __name__ == "__main__":
    main()
