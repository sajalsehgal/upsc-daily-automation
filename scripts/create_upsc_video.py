"""
Create UPSC video - BRIGHT clean backgrounds, NO flag
"""
import os
import subprocess
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import time
import html
import requests
import random

load_dotenv()

class UPSCVideoCreator:
    def __init__(self):
        self.width = 1920
        self.height = 1080
        
        self.speech_key = os.getenv('AZURE_SPEECH_KEY')
        self.speech_region = os.getenv('AZURE_SPEECH_REGION')
        self.pexels_key = os.getenv('PEXELS_API_KEY')
        
        if not self.speech_key or not self.speech_region:
            raise Exception("Azure credentials not found")
        
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key,
            region=self.speech_region
        )
        
        self.speech_config.speech_synthesis_voice_name = 'hi-IN-MadhurNeural'
        self.speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )
    
    def get_news_background_from_pexels(self, output_path):
        """Get bright professional background - NO FLAG"""
        
        if not self.pexels_key:
            return self.create_professional_gradient(output_path)
        
        # Professional news/business queries - NO FLAG
        queries = [
            "mumbai skyline sunset",
            "delhi modern architecture",
            "bangalore tech city night",
            "india modern cityscape",
            "business district night",
            "urban skyline india",
            "modern india buildings",
            "indian metro city lights"
        ]
        
        query = random.choice(queries)
        
        print(f"   Fetching: '{query}'...")
        
        try:
            headers = {"Authorization": self.pexels_key}
            response = requests.get(
                f"https://api.pexels.com/v1/search?query={query}&orientation=landscape&per_page=15",
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return self.create_professional_gradient(output_path)
            
            data = response.json()
            
            if not data.get('photos'):
                return self.create_professional_gradient(output_path)
            
            photo = random.choice(data['photos'])
            image_url = photo['src']['large2x']
            
            img_response = requests.get(image_url, timeout=10)
            img_path = output_path.replace('.png', '_temp.jpg')
            
            with open(img_path, 'wb') as f:
                f.write(img_response.content)
            
            print(f"   ✅ Downloaded")
            
            return self.process_background_bright(img_path, output_path)
            
        except Exception as e:
            return self.create_professional_gradient(output_path)
    
    def process_background_bright(self, image_path, output_path):
        """Process image - BRIGHT and CLEAN"""
        
        img = Image.open(image_path)
        
        # Resize to exact dimensions
        img_ratio = img.width / img.height
        target_ratio = self.width / self.height
        
        if img_ratio > target_ratio:
            new_height = self.height
            new_width = int(new_height * img_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            left = (new_width - self.width) // 2
            img = img.crop((left, 0, left + self.width, self.height))
        else:
            new_width = self.width
            new_height = int(new_width / img_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            top = (new_height - self.height) // 2
            img = img.crop((0, top, self.width, top + self.height))
        
        # Keep it BRIGHT - only slight darkening
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.65)  # 65% brightness - much brighter!
        
        # Light overlay for subtle effect
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 100))  # Light overlay
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        img = img.convert('RGB')
        
        # Tricolor borders - thicker and prominent
        draw = ImageDraw.Draw(img)
        border = 35
        draw.rectangle([(0, 0), (self.width, border)], fill='#FF9933')
        draw.rectangle([(0, border), (self.width, border * 2)], fill='#FFFFFF')
        draw.rectangle([(0, self.height - border * 2), (self.width, self.height - border)], fill='#FFFFFF')
        draw.rectangle([(0, self.height - border), (self.width, self.height)], fill='#138808')
        
        img.save(output_path, quality=95)
        print(f"   ✅ Bright clean background")
        return output_path
    
    def create_professional_gradient(self, output_path):
        """Professional gradient - bright and clean"""
        img = Image.new('RGB', (self.width, self.height), color='#1a2540')
        draw = ImageDraw.Draw(img)
        
        # Brighter gradient
        for y in range(self.height):
            r = int(26 + (45 - 26) * (y / self.height))
            g = int(37 + (60 - 37) * (y / self.height))
            b = int(64 + (90 - 64) * (y / self.height))
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        # Tricolor borders
        border = 35
        draw.rectangle([(0, 0), (self.width, border)], fill='#FF9933')
        draw.rectangle([(0, border), (self.width, border * 2)], fill='#FFFFFF')
        draw.rectangle([(0, self.height - border * 2), (self.width, self.height - border)], fill='#FFFFFF')
        draw.rectangle([(0, self.height - border), (self.width, self.height)], fill='#138808')
        
        img.save(output_path, quality=95)
        return output_path
    
    def create_thumbnail(self, date_str, output_path):
        """Thumbnail - simple and clean"""
        img = Image.new('RGB', (1280, 720), color='#1a2540')
        draw = ImageDraw.Draw(img)
        
        # Gradient background
        for y in range(720):
            r = int(26 + (45 - 26) * (y / 720))
            g = int(37 + (60 - 37) * (y / 720))
            b = int(64 + (90 - 64) * (y / 720))
            draw.line([(0, y), (1280, y)], fill=(r, g, b))
        
        # Tricolor borders
        border = 25
        draw.rectangle([(0, 0), (1280, border)], fill='#FF9933')
        draw.rectangle([(0, border), (1280, border * 2)], fill='#FFFFFF')
        draw.rectangle([(0, 720 - border * 2), (1280, 720 - border)], fill='#FFFFFF')
        draw.rectangle([(0, 720 - border), (1280, 720)], fill='#138808')
        
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 100)
            date_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 60)
        except:
            title_font = date_font = ImageFont.load_default()
        
        # Title with shadow
        title_text = "Daily Current Affairs"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_w = title_bbox[2] - title_bbox[0]
        title_x = (1280 - title_w) // 2
        
        draw.text((title_x + 4, 284), title_text, font=title_font, fill=(0, 0, 0))
        draw.text((title_x, 280), title_text, font=title_font, fill=(255, 255, 255))
        
        # Date
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        date_display = date_obj.strftime('%d %B %Y')
        date_bbox = draw.textbbox((0, 0), date_display, font=date_font)
        date_w = date_bbox[2] - date_bbox[0]
        date_x = (1280 - date_w) // 2
        
        draw.text((date_x + 3, 423), date_display, font=date_font, fill=(0, 0, 0))
        draw.text((date_x, 420), date_display, font=date_font, fill=(255, 200, 80))
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path, quality=95)
        return output_path
    
    def split_text_into_chunks(self, text, max_chars=4000):
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        chunks = []
        current = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_with_period = sentence + ". "
            
            if len(current) + len(sentence_with_period) > max_chars:
                if current:
                    chunks.append(current.strip())
                current = sentence_with_period
            else:
                current += sentence_with_period
        
        if current:
            chunks.append(current.strip())
        
        return chunks
    
    def generate_audio_chunk(self, text, output_path):
        try:
            text = html.escape(text)
            audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            ssml = f"""
            <speak version='1.0' xml:lang='hi-IN'>
                <voice name='hi-IN-MadhurNeural'>
                    <prosody rate='0.88' pitch='+0%'>
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
            
            result = synthesizer.speak_ssml_async(ssml).get()
            return result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted
                
        except Exception as e:
            return False
    
    def generate_audio(self, script, output_path):
        print("\n🎙️  Generating audio...")
        
        os.makedirs("output/upsc/chunks", exist_ok=True)
        
        chunks = self.split_text_into_chunks(script, max_chars=4000)
        print(f"   Chunks: {len(chunks)}")
        
        chunk_files = []
        
        for i, chunk in enumerate(chunks, 1):
            chunk_file = f"output/upsc/chunks/chunk_{i:03d}.mp3"
            print(f"   Chunk {i}/{len(chunks)}...", end=' ')
            
            if not self.generate_audio_chunk(chunk, chunk_file):
                print("✗")
                continue
            
            chunk_files.append(chunk_file)
            print("✓")
            time.sleep(2)
        
        if not chunk_files:
            return False
        
        print(f"\n   Combining...")
        
        if len(chunk_files) == 1:
            subprocess.run(['cp', chunk_files[0], output_path], check=True)
        else:
            concat_list = "output/upsc/chunks/concat_list.txt"
            with open(concat_list, "w") as f:
                for cf in chunk_files:
                    f.write(f"file '{os.path.abspath(cf)}'\n")
            
            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", concat_list, "-c", "copy", output_path
            ], check=True, capture_output=True)
        
        print(f"✅ Audio: {os.path.getsize(output_path)/(1024*1024):.1f} MB")
        return True
    
    def create_video(self, audio_path, background_path, output_path):
        print("\n🎬 Creating video...")
        
        subprocess.run([
            'ffmpeg', '-y', '-loop', '1', '-i', background_path,
            '-i', audio_path, '-c:v', 'libx264', '-tune', 'stillimage',
            '-c:a', 'aac', '-b:a', '192k', '-pix_fmt', 'yuv420p',
            '-shortest', output_path
        ], check=True, capture_output=True)
        
        print(f"✅ Video: {os.path.getsize(output_path)/(1024*1024):.1f} MB")
        return output_path
    
    def create_complete_video(self, script_path, date_str):
        print(f"\n{'='*70}")
        print(f"  UPSC Video - {date_str}")
        print(f"{'='*70}")
        
        with open(script_path, 'r', encoding='utf-8') as f:
            script = f.read()
        
        for dirname in ['audio', 'backgrounds', 'videos', 'thumbnails', 'chunks']:
            os.makedirs(f'output/upsc/{dirname}', exist_ok=True)
        
        audio_path = f'output/upsc/audio/audio_{date_str}.mp3'
        bg_path = f'output/upsc/backgrounds/bg_{date_str}.png'
        video_path = f'output/upsc/videos/current_affairs_{date_str}.mp4'
        thumb_path = f'output/upsc/thumbnails/thumb_{date_str}.png'
        
        if not self.generate_audio(script, audio_path):
            return None
        
        print("\n🖼️  Creating background...")
        self.get_news_background_from_pexels(bg_path)
        self.create_thumbnail(date_str, thumb_path)
        
        self.create_video(audio_path, bg_path, video_path)
        
        print(f"\n{'='*70}")
        print("  🎉 COMPLETE!")
        print(f"{'='*70}")
        
        return {
            'video': video_path,
            'thumbnail': thumb_path,
            'audio': audio_path
        }

def main():
    date_str = datetime.now().strftime('%Y-%m-%d')
    script_path = f'output/upsc/scripts/script_{date_str}.txt'
    
    if not os.path.exists(script_path):
        print(f"❌ Script not found")
        return
    
    creator = UPSCVideoCreator()
    creator.create_complete_video(script_path, date_str)

if __name__ == "__main__":
    main()
