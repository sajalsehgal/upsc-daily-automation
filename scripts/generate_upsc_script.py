"""
Generate UPSC script - REAL detailed Hindi news explanations
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import time

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
    
    def generate_single_news_item(self, news_article, item_number):
        """Generate ONE detailed news in PURE Hindi"""
        
        news_numbers_hindi = ["पहली", "दूसरी", "तीसरी", "चौथी", "पांचवीं", 
                             "छठी", "सातवीं", "आठवीं", "नौवीं", "दसवीं"]
        
        title = news_article.get('title', '')
        summary = news_article.get('summary', '')[:1000]
        
        prompt = f"""You are a UPSC teacher explaining news in conversational Hindi to students.

English News: {title}
Details: {summary}

Write EXACTLY 150-180 words in conversational Hindi:

{news_numbers_hindi[item_number-1]} खबर।
[Translate the title to simple Hindi first, then explain in 7-8 complete sentences:
- What exactly happened (translate all English content to Hindi)
- Who was involved (names can stay in English, everything else in Hindi)
- Where and when did it happen
- Why is this important for students
- What are the key facts
- What could be the implications
DO NOT use generic phrases like "mahatvapurna jankari mili hai" or "khabar jaldi milegi"
DO NOT say "UPSC mein pucha ja sakta hai" at the end
Just explain the news naturally like a teacher explaining to students in a classroom]

CRITICAL RULES:
1. Write EVERYTHING in Hindi except:
   - Proper names (people, organizations, places)
   - Acronyms (WHO, NATO, GDP, etc.)
2. DO NOT translate the English headline as-is - explain it naturally in Hindi
3. DO NOT use filler phrases or generic statements
4. Focus on ACTUAL NEWS DETAILS from the summary
5. 150-180 words minimum
6. Conversational tone - like talking to a friend
7. DO NOT end with "UPSC mein pucha ja sakta hai" - just give facts

Write detailed Hindi explanation now:"""

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.9,
                "maxOutputTokens": 1000
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=120)
            
            if response.status_code != 200:
                print(f" ❌")
                return self.create_better_fallback(news_article, item_number)
            
            result = response.json()
            
            if 'candidates' not in result or not result['candidates']:
                print(f" ❌")
                return self.create_better_fallback(news_article, item_number)
            
            candidate = result['candidates'][0]
            
            if 'content' not in candidate or 'parts' not in candidate['content']:
                print(f" ❌")
                return self.create_better_fallback(news_article, item_number)
            
            text = candidate['content']['parts'][0]['text'].strip()
            
            # Check quality
            word_count = len(text.split())
            
            # Remove the UPSC line if Gemini added it
            if "UPSC" in text or "upsc" in text or "पूछा जा सकता है" in text:
                lines = text.split('\n')
                text = '\n'.join([line for line in lines if 'UPSC' not in line and 'upsc' not in line and 'पूछा जा सकता है' not in line])
            
            if word_count < 100:
                print(f" ⚠️  ({word_count}w)")
                return self.create_better_fallback(news_article, item_number)
            
            return text
            
        except Exception as e:
            print(f" ❌")
            return self.create_better_fallback(news_article, item_number)
    
    def create_better_fallback(self, news_article, item_number):
        """Better fallback with actual content"""
        news_numbers_hindi = ["पहली", "दूसरी", "तीसरी", "चौथी", "पांचवीं", 
                             "छठी", "सातवीं", "आठवीं", "नौवीं", "दसवीं"]
        
        title = news_article.get('title', 'समाचार')
        summary = news_article.get('summary', '')[:300]
        
        # At least provide some content
        return f"""{news_numbers_hindi[item_number-1]} खबर।
{title}। यह खबर हाल ही में सामने आई है। {summary if summary else 'विस्तृत जानकारी शीघ्र उपलब्ध होगी।'}"""
    
    def generate_hindi_script(self, news_data):
        """Generate complete detailed Hindi script"""
        
        articles = news_data['articles']
        date_hindi = news_data.get('date_hindi', datetime.now().strftime('%d %B %Y'))
        
        print("\n🤖 Generating detailed Hindi script...")
        print("   Creating natural explanations...\n")
        
        # Intro
        intro = f"""नमस्ते दोस्तों! आज की तारीख है {date_hindi}। आज हम देखेंगे Top 10 Current Affairs जो आपकी UPSC और सरकारी परीक्षा की तैयारी के लिए बहुत महत्वपूर्ण हैं। हर खबर को मैं विस्तार से समझाऊंगा। तो चलिए शुरू करते हैं।

"""
        
        # Generate 10 news items
        news_items = []
        for i in range(10):
            print(f"   News {i+1}/10...", end='')
            
            if i < len(articles):
                item = self.generate_single_news_item(articles[i], i+1)
                news_items.append(item)
                print(" ✓")
            else:
                print(" ⚠️")
                break
            
            if i < 9:
                time.sleep(3)
        
        # Outro
        outro = """

तो दोस्तों, यह थे आज के Top 10 Current Affairs। Description में PDF notes का link मिलेगा। अगर video helpful लगा तो like करें, share करें, और channel को subscribe करना मत भूलिए। Bell icon भी दबा दें। कल फिर मिलेंगे नई खबरों के साथ। धन्यवाद!"""
        
        # Combine
        script = intro + "\n\n".join(news_items) + outro
        
        word_count = len(script.split())
        
        print(f"\n✅ Script generated!")
        print(f"   News items: {len(news_items)}")
        print(f"   Words: {word_count}")
        print(f"   Duration: ~{word_count / 130:.1f} minutes")
        
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

if __name__ == "__main__":
    main()
