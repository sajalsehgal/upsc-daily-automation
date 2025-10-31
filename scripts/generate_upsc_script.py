"""
Generate UPSC current affairs script in Hindi using Google Gemini REST API
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class UPSCScriptGenerator:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise Exception("GEMINI_API_KEY not found in environment")
        
        # Use v1 API with gemini-2.5-flash (latest free model)
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
        
        # Prepare news summary with more details
        news_summary = "\n\n".join([
            f"{i+1}. Title: {article['title']}\n   Summary: {article.get('summary', 'No summary')}\n   Source: {article.get('source', 'Unknown')}"
            for i, article in enumerate(articles[:30])
        ])
        
        prompt = f"""आप एक UPSC Current Affairs educator हैं। आपको आज की Top 10 news items को Hindi में एक YouTube video script बनानी है।

आज की तारीख: {date_hindi}

Available News Articles ({len(articles)} articles from multiple sources):
{news_summary}

INSTRUCTIONS:
1. ऊपर दिए गए articles में से सबसे महत्वपूर्ण 10 news items select करें जो UPSC के लिए relevant हों
2. Priority दें:
   - Government policies & schemes (नई योजनाएं, नीतियां)
   - International relations (विदेश नीति, संधियाँ)
   - Economy & budget (आर्थिक नीति, बजट)
   - Environment & climate (पर्यावरण, जलवायु परिवर्तन)
   - Science & technology (विज्ञान, तकनीक)
   - Social issues (सामाजिक मुद्दे)
   - Important appointments (महत्वपूर्ण नियुक्तियां)
   - Supreme Court judgments (सुप्रीम कोर्ट के फैसले)
   - Awards & recognition (पुरस्कार, सम्मान)

3. हर news item के लिए (3-4 sentences):
   - क्या हुआ? (What happened - be specific with facts, dates, names)
   - क्यों important है? (Why important for UPSC)
   - UPSC में कहाँ पूछा जा सकता है? (Prelims/Mains/Essay - specific paper/topic)
   - Key facts/dates/names/numbers highlight करें

4. SCRIPT FORMAT:

[INTRO - 30 seconds]
नमस्ते दोस्तों! आज की तारीख है {date_hindi}। 
आज हम देखेंगे Top 10 Current Affairs जो आपकी UPSC और सरकारी परीक्षा की तैयारी के लिए बहुत जरूरी हैं।
तो चलिए शुरू करते हैं।

[NEWS ITEM 1 - 60-90 seconds]
पहली खबर: [Title in simple, clear Hindi]
[Detailed explanation in 3-4 sentences with specific facts]
UPSC Relevance: [Detailed - which paper, which topic, example question type]

[NEWS ITEM 2 - 60-90 seconds]
दूसरी खबर: [Title]
[Explanation]
UPSC Relevance: [...]

... [Continue for all 10 items - each 60-90 seconds]

[OUTRO - 30 seconds]
तो दोस्तों, यह थे आज के Top 10 Current Affairs। 
PDF notes और detailed analysis के लिए description में link देखें।
अगर video helpful लगा तो like करें, share करें और channel को subscribe करना मत भूलिए।
Bell icon भी press कर दें ताकि आपको रोज़ सुबह 7 बजे notification मिल जाए।
कल फिर मिलेंगे नई खबरों के साथ। तब तक के लिए, पढ़ते रहिए। धन्यवाद!

5. LANGUAGE GUIDELINES:
   - Simple, conversational Hindi (not overly formal)
   - Devanagari script only
   - Use English terms when commonly used (GDP, NASA, WHO, etc.)
   - Avoid complex Sanskrit/Urdu words
   - Make it engaging like you're talking to a friend
   - Include specific numbers, dates, names whenever available
   - Total script should be 10-12 minutes (about 1400-1600 words)

6. QUALITY REQUIREMENTS:
   - Each news item must have concrete facts (dates, numbers, names)
   - Avoid vague statements
   - Connect each news to specific UPSC syllabus topics
   - Make it actionable for students

Generate the complete detailed script now:"""

        print("\n🤖 Generating Hindi script with Gemini 2.5 Flash...")
        print("   This will take 30-60 seconds...")
        
        # Make API request
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 8192
            }
        }
        
        response = requests.post(self.api_url, json=payload, timeout=120)
        
        if response.status_code != 200:
            raise Exception(f"Gemini API error: {response.status_code} - {response.text}")
        
        result = response.json()
        script = result['candidates'][0]['content']['parts'][0]['text']
        
        print("✅ Script generated!")
        print(f"   Length: {len(script)} characters")
        
        return script
    
    def save_script(self, script, output_path):
        """Save generated script"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(script)
        
        print(f"💾 Script saved: {output_path}")
        return script

def main():
    # Load today's news
    date_str = datetime.now().strftime('%Y-%m-%d')
    news_file = f'output/upsc/news/daily_news_{date_str}.json'
    
    if not os.path.exists(news_file):
        print(f"❌ News file not found: {news_file}")
        print("   Run scrape_news.py first!")
        return
    
    # Generate script
    generator = UPSCScriptGenerator()
    news_data = generator.load_news(news_file)
    
    print(f"\n📰 Loaded {news_data['total_articles']} articles")
    print(f"   Date: {news_data['date_hindi']}")
    print(f"   Sources: {news_data.get('sources_count', 'N/A')}")
    
    script = generator.generate_hindi_script(news_data)
    
    # Save script
    output_path = f'output/upsc/scripts/script_{date_str}.txt'
    generator.save_script(script, output_path)
    
    print(f"\n📝 Script preview (first 500 chars):")
    print("-" * 70)
    print(script[:500] + "...")
    print("-" * 70)
    
    print(f"\n🎉 Script generation complete!")

if __name__ == "__main__":
    main()
