"""
Generate UPSC script - DETAILED Hindi explanations
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
        """Generate ONE detailed news explanation"""
        
        news_numbers_hindi = ["पहली", "दूसरी", "तीसरी", "चौथी", "पांचवीं", 
                             "छठी", "सातवीं", "आठवीं", "नौवीं", "दसवीं"]
        
        title = news_article.get('title', '')
        summary = news_article.get('summary', '')[:800]  # Use more of summary
        
        prompt = f"""You are a UPSC educator. Explain this news in DETAILED Hindi (NOT just headline).

News: {title}
Details: {summary}

Write EXACTLY 120-150 words in this format:

{news_numbers_hindi[item_number-1]} खबर।
[Write a DETAILED explanation in 6-7 complete Hindi sentences covering:
- What exactly happened (specific details)
- Who was involved (names, positions)
- Where did it happen (locations)
- When did it happen (dates if available)
- Why is it important for India/world
- What are the implications
- Key facts students should remember]
UPSC में यह General Studies Paper 1, 2, या 3 में [specific topic like अंतर्राष्ट्रीय संबंध, भारतीय अर्थव्यवस्था, पर्यावरण, विज्ञान और प्रौद्योगिकी, शासन] से पूछा जा सकता है।

CRITICAL RULES:
- Write in SIMPLE CONVERSATIONAL HINDI (like talking to a friend)
- Do NOT just translate the English headline
- EXPLAIN the news in detail
- Use Hindi for everything except proper nouns (WHO, NASA, GDP, names)
- Must be 120-150 words
- Write as if you're a teacher explaining to students

Write the detailed explanation now:"""

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 800
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=90)
            
            if response.status_code != 200:
                print(f" ❌ API Error")
                return self.create_fallback_item(news_article, item_number)
            
            result = response.json()
            
            if 'candidates' not in result or not result['candidates']:
                print(f" ❌ No response")
                return self.create_fallback_item(news_article, item_number)
            
            candidate = result['candidates'][0]
            
            if 'content' not in candidate or 'parts' not in candidate['content']:
                print(f" ❌ Invalid format")
                return self.create_fallback_item(news_article, item_number)
            
            text = candidate['content']['parts'][0]['text'].strip()
            
            # Verify it's actually in Hindi and detailed
            word_count = len(text.split())
            if word_count < 80:
                print(f" ⚠️  Too short ({word_count} words), retrying...")
                time.sleep(2)
                # Retry once
                response = requests.post(self.api_url, json=payload, timeout=90)
                if response.status_code == 200:
                    result = response.json()
                    if 'candidates' in result and result['candidates']:
                        text = result['candidates'][0]['content']['parts'][0]['text'].strip()
            
            return text
            
        except Exception as e:
            print(f" ❌ Exception: {e}")
            return self.create_fallback_item(news_article, item_number)
    
    def create_fallback_item(self, news_article, item_number):
        """Create a basic fallback if API fails"""
        news_numbers_hindi = ["पहली", "दूसरी", "तीसरी", "चौथी", "पांचवीं", 
                             "छठी", "सातवीं", "आठवीं", "नौवीं", "दसवीं"]
        
        return f"""{news_numbers_hindi[item_number-1]} खबर।
{news_article.get('title', 'समाचार')} के बारे में आज महत्वपूर्ण जानकारी मिली है। यह खबर भारत और अंतर्राष्ट्रीय संबंधों के लिए महत्वपूर्ण है। विस्तृत जानकारी जल्द ही उपलब्ध होगी।
UPSC में यह सामान्य अध्ययन से पूछा जा सकता है।"""
    
    def generate_hindi_script(self, news_data):
        """Generate complete detailed script"""
        
        articles = news_data['articles']
        date_hindi = news_data.get('date_hindi', datetime.now().strftime('%d %B %Y'))
        
        print("\n🤖 Generating DETAILED Hindi script...")
        print("   Creating comprehensive explanations...\n")
        
        # Intro
        intro = f"""नमस्ते दोस्तों! आज की तारीख है {date_hindi}। आज हम देखेंगे Top 10 Current Affairs जो आपकी UPSC और सरकारी परीक्षा की तैयारी के लिए बहुत जरूरी हैं। हर खबर को मैं विस्तार से समझाऊंगा। तो चलिए शुरू करते हैं।

"""
        
        # Generate 10 detailed news items
        news_items = []
        for i in range(10):
            print(f"   News {i+1}/10...", end='')
            
            if i < len(articles):
                item = self.generate_single_news_item(articles[i], i+1)
                news_items.append(item)
                print(" ✓")
            else:
                print(" ⚠️  No article")
                break
            
            # Delay between requests
            if i < 9:
                time.sleep(3)  # Longer delay to avoid rate limits
        
        # Outro
        outro = """

तो दोस्तों, यह थे आज के Top 10 Current Affairs जो मैंने विस्तार से समझाए। PDF notes के लिए description में link देखें। अगर video helpful लगा तो like करें, share करें, और channel को subscribe करना मत भूलिए। Bell icon भी press कर दें ताकि रोज़ notification मिल जाए। कल फिर मिलेंगे नई खबरों के साथ। तब तक के लिए, पढ़ते रहिए। धन्यवाद!"""
        
        # Combine
        script = intro + "\n\n".join(news_items) + outro
        
        word_count = len(script.split())
        
        print(f"\n✅ Detailed script generated!")
        print(f"   News items: {len(news_items)}")
        print(f"   Total words: {word_count}")
        print(f"   Est. duration: {word_count / 130:.1f} minutes")
        
        if word_count < 1500:
            print(f"   ⚠️  Warning: Script might be too short!")
        
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
    print(script[:700])
    print("-" * 70)

if __name__ == "__main__":
    main()
