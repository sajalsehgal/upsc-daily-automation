"""
Generate UPSC current affairs script in Hindi using Google Gemini REST API
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
            raise Exception("GEMINI_API_KEY not found in environment")
        
        self.api_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={self.api_key}"
    
    def load_news(self, news_file):
        """Load scraped news"""
        with open(news_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    def generate_hindi_script(self, news_data):
        """Generate Hindi script for UPSC current affairs video"""
        
        articles = news_data['articles']
        date_hindi = news_data.get('date_hindi', datetime.now().strftime('%d %B %Y'))
        
        news_summary = "\n\n".join([
            f"{i+1}. Title: {article['title']}\n   Summary: {article.get('summary', 'No summary')}\n   Source: {article.get('source', 'Unknown')}"
            for i, article in enumerate(articles[:40])
        ])
        
        prompt = f"""You are a UPSC Current Affairs educator. Create a Hindi YouTube video script covering exactly 10 news items.

Today's Date: {date_hindi}

Available News Articles ({len(articles)} articles):
{news_summary}

CRITICAL REQUIREMENTS:

1. Select the 10 MOST IMPORTANT news items relevant for UPSC
2. Each news item MUST be 4-5 sentences (at least 60-80 words per item)
3. Include specific details: names, dates, numbers, locations
4. Total script must be 1800-2200 words for 12-15 minutes

EXACT FORMAT (copy this structure exactly):

नमस्ते दोस्तों! आज की तारीख है {date_hindi}। आज हम देखेंगे Top 10 Current Affairs जो आपकी UPSC और सरकारी परीक्षा की तैयारी के लिए बहुत जरूरी हैं। तो चलिए शुरू करते हैं।

पहली खबर।
[Write 4-5 complete sentences about first news with all details - names, dates, locations, numbers]
UPSC के Prelims और Mains में यह [specific topic/subject] से पूछा जा सकता है।

दूसरी खबर।
[Write 4-5 complete sentences about second news with all details]
UPSC के Prelims और Mains में यह [specific topic/subject] से पूछा जा सकता है।

तीसरी खबर।
[Write 4-5 complete sentences about third news with all details]
UPSC के Prelims और Mains में यह [specific topic/subject] से पूछा जा सकता है।

चौथी खबर।
[Write 4-5 complete sentences about fourth news with all details]
UPSC के Prelims और Mains में यह [specific topic/subject] से पूछा जा सकता है।

पांचवीं खबर।
[Write 4-5 complete sentences about fifth news with all details]
UPSC के Prelims और Mains में यह [specific topic/subject] से पूछा जा सकता है।

छठी खबर।
[Write 4-5 complete sentences about sixth news with all details]
UPSC के Prelims और Mains में यह [specific topic/subject] से पूछा जा सकता है।

सातवीं खबर।
[Write 4-5 complete sentences about seventh news with all details]
UPSC के Prelims और Mains में यह [specific topic/subject] से पूछा जा सकता है।

आठवीं खबर।
[Write 4-5 complete sentences about eighth news with all details]
UPSC के Prelims और Mains में यह [specific topic/subject] से पूछा जा सकता है।

नौवीं खबर।
[Write 4-5 complete sentences about ninth news with all details]
UPSC के Prelims और Mains में यह [specific topic/subject] से पूछा जा सकता है।

दसवीं खबर।
[Write 4-5 complete sentences about tenth news with all details]
UPSC के Prelims और Mains में यह [specific topic/subject] से पूछा जा सकता है।

तो दोस्तों, यह थे आज के Top 10 Current Affairs। PDF notes और detailed analysis के लिए description में link देखें। अगर video helpful लगा तो like करें और channel को subscribe करना मत भूलिए। Bell icon press कर दें। कल फिर मिलेंगे। धन्यवाद!

RULES:
- Write ONLY the actual spoken Hindi content
- NO metadata like [INTRO], [NEWS ITEM 1], etc.
- Each news MUST have 4-5 detailed sentences
- Include all specific facts available
- Use simple conversational Hindi
- MUST generate all 10 news items completely
- Total length: 1800-2200 words

Generate the complete script now:"""

        print("\n🤖 Generating script with Gemini...")
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 16384,
                "topP": 0.95
            }
        }
        
        response = requests.post(self.api_url, json=payload, timeout=180)
        
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code} - {response.text}")
        
        result = response.json()
        script = result['candidates'][0]['content']['parts'][0]['text']
        
        # Count news items
        news_count = script.count('खबर।')
        word_count = len(script.split())
        
        print(f"✅ Script generated!")
        print(f"   News items detected: {news_count}")
        print(f"   Total words: {word_count}")
        print(f"   Characters: {len(script)}")
        
        if news_count < 10:
            print(f"   ⚠️  Warning: Only {news_count} news items found (expected 10)")
        
        return script
    
    def save_script(self, script, output_path):
        """Save generated script"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(script)
        
        print(f"💾 Saved: {output_path}")
        return script

def main():
    date_str = datetime.now().strftime('%Y-%m-%d')
    news_file = f'output/upsc/news/daily_news_{date_str}.json'
    
    if not os.path.exists(news_file):
        print(f"❌ News file not found: {news_file}")
        return
    
    generator = UPSCScriptGenerator()
    news_data = generator.load_news(news_file)
    
    print(f"\n📰 Loaded {news_data['total_articles']} articles")
    
    script = generator.generate_hindi_script(news_data)
    
    output_path = f'output/upsc/scripts/script_{date_str}.txt'
    generator.save_script(script, output_path)
    
    print(f"\n📝 Preview:")
    print("-" * 70)
    print(script[:500] + "...")
    print("-" * 70)

if __name__ == "__main__":
    main()
