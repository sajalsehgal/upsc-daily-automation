"""
Generate UPSC script using OpenAI GPT-4o-mini (RELIABLE)
"""
import os
import json
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
import time

load_dotenv()

class UPSCScriptGenerator:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise Exception("OPENAI_API_KEY not found in .env")
        
        self.client = OpenAI(api_key=api_key)
    
    def load_news(self, news_file):
        with open(news_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_hindi_script(self, news_data):
        """Generate complete Hindi script with OpenAI"""
        
        articles = news_data['articles'][:15]  # Use top 15 articles
        date_hindi = news_data.get('date_hindi', datetime.now().strftime('%d %B %Y'))
        
        # Prepare article summaries
        articles_text = "\n\n".join([
            f"Article {i+1}:\nTitle: {article['title']}\nSummary: {article.get('summary', '')[:600]}\nSource: {article.get('source', '')}"
            for i, article in enumerate(articles)
        ])
        
        prompt = f"""You are a UPSC Current Affairs educator. Create a Hindi video script for YouTube.

Date: {date_hindi}

Available News Articles:
{articles_text}

YOUR TASK:
Select the 10 MOST IMPORTANT news items for UPSC students and create a DETAILED Hindi script.

SCRIPT FORMAT:

नमस्ते दोस्तों! आज की तारीख है {date_hindi}। आज हम देखेंगे Top 10 Current Affairs जो आपकी UPSC परीक्षा के लिए बहुत महत्वपूर्ण हैं। तो चलिए शुरू करते हैं।

पहली खबर।
[Write 6-7 sentences in FLUENT CONVERSATIONAL HINDI explaining:
- What happened (translate the English news to natural Hindi)
- Who is involved (names can stay in English)
- Where and when
- Why it matters
- Key facts
- Context and implications
Write 150-180 words in pure Hindi - like a teacher explaining to students]

दूसरी खबर।
[Same format - 150-180 words detailed Hindi explanation]

तीसरी खबर।
[Same format]

चौथी खबर।
[Same format]

पांचवीं खबर।
[Same format]

छठी खबर।
[Same format]

सातवीं खबर।
[Same format]

आठवीं खबर।
[Same format]

नौवीं खबर।
[Same format]

दसवीं खबर।
[Same format]

तो दोस्तों, यह थे आज के Top 10 Current Affairs। Description में PDF notes का link मिलेगा। Video पसंद आए तो like और subscribe करें। Bell icon दबाना मत भूलिए। कल फिर मिलेंगे। धन्यवाद!

CRITICAL RULES:
1. Write EVERYTHING in Hindi except proper nouns (names, places, organizations)
2. Translate English news naturally to Hindi - don't just read English titles
3. NO filler phrases like "ye khabar haal hi mein saamne aayi hai"
4. NO generic statements like "mahatvapurna jankari mili hai"
5. NO "UPSC mein pucha ja sakta hai" after each news
6. Each news item: 150-180 words of ACTUAL DETAILS
7. Conversational Hindi - like talking to students
8. Focus on FACTS, not fluff
9. Total script: 1800-2200 words

Generate the COMPLETE script now with ALL 10 detailed news items:"""

        print("\n🤖 Generating detailed Hindi script with OpenAI...")
        print("   This will take 45-90 seconds...")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a UPSC educator who creates detailed Hindi video scripts. You always follow instructions precisely and write in fluent conversational Hindi."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=4000
            )
            
            script = response.choices[0].message.content.strip()
            
            word_count = len(script.split())
            
            print(f"✅ Script generated!")
            print(f"   Words: {word_count}")
            print(f"   Duration: ~{word_count / 130:.1f} minutes")
            
            if word_count < 1500:
                print(f"   ⚠️  Script seems short, but continuing...")
            
            return script
            
        except Exception as e:
            print(f"❌ OpenAI Error: {e}")
            raise
    
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
    
    print(f"\n📝 First 700 characters:")
    print("-" * 70)
    print(script[:700])
    print("-" * 70)

if __name__ == "__main__":
    main()
