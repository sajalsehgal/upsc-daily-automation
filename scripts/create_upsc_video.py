"""
Create video with 1.25x speed and bright backgrounds
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
    
    def get_background(self, output_path):
        """Get bright professional background"""
        
        if not self.pexels_key:
            return self.create_gradient(output_path)
        
        queries = [
            "mumbai skyline sunset",
            "delhi skyline evening",
            "bangalore tech city",
            "modern india cityscape",
            "business district lights"
        ]
        
        query = random.choice(queries)
        
        try:
            headers = {"Authorization": self.pexels_key}
            response = requests.get(
                f"https://api.pexels.com/v1/search?query={query}&orientation=landscape&per_page=10",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('photos'):
                    photo = random.choice(data['photos'])
                    image_url = photo['src']['large2x']
                    
                    img_response = requests.get(image_url, timeout=10)
                    img_path = output_path.replace('.png', '_temp.jpg')
                    
                    with open(img_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    return self.process_image(img_path, output_path)
        except:
            pass
        
        return self.create_gradient(output_path)
    
    def process_image(self, img_path, output_path):
        """Process image - bright and clean"""
        img = Image.open(img_path)
        
        # Resize and crop
        img_ratio = img.width / img.height
        if img_ratio > 16/9:
            new_h = self.height
            new_w = int(new_h * img_ratio)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            left = (new_w - self.width) // 2
            img = img.crop((left, 0, left + self.width, self.height))
        else:
            new_w = self.width
            new_h = int(new_w / img_ratio)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            top = (new_h - self.height) // 2
            img = img.crop((0, top, self.width, top + self.height))
        
        # Darken slightly (65% brightness)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.65)
        
        # Light overlay
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 100))
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        img = img.convert('RGB')
        
        # Tricolor borders
        draw = ImageDraw.Draw(img)
        b = 35
        draw.rectangle([(0, 0), (self.width, b)], fill='#FF9933')
        draw.rectangle([(0, b), (self.width, b*2)], fill='#FFFFFF')
        draw.rectangle([(0, self.height-b*2), (self.width, self.height-b)], fill='#FFFFFF')
        draw.rectangle([(0, self.height-b), (self.width, self.height)], fill='#138808')
        
        img.save(output_path, quality=95)
        return output_path
    
    def create_gradient(self, output_path):
        """Bright gradient background"""
        img = Image.new('RGB', (self.width, self.height), '#1a2540')
        draw = ImageDraw.Draw(img)
        
        for y in range(self.height):
            r = int(26 + (50 - 26) * (y / self.height))
            g = int(37 + (65 - 37) * (y / self.height))
            b = int(64 + (95 - 64) * (y / self.height))
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        b = 35
        draw.rectangle([(0, 0), (self.width, b)], fill='#FF9933')
        draw.rectangle([(0, b), (self.width, b*2)], fill='#FFFFFF')
        draw.rectangle([(0, self.height-b*2), (self.width, self.height-b)], fill='#FFFFFF')
        draw.rectangle([(0, self.height-b), (self.width, self.height)], fill='#138808')
        
        img.save(output_path, quality=95)
        return output_path
    
    def create_thumbnail(self, date_str, output_path):
        """Simple thumbnail"""
        img = Image.new('RGB', (1280, 720), '#1a2540')
        draw = ImageDraw.Draw(img)
        
        for y in range(720):
            r = int(26 + (50 - 26) * (y / 720))
            g = int(37 + (65 - 37) * (y / 720))
            b = int(64 + (95 - 64) * (y / 720))
            draw.line([(0, y), (1280, y)], fill=(r, g, b))
        
        b = 25
        draw.rectangle([(0, 0), (1280, b)], fill='#FF9933')
        draw.rectangle([(0, b), (1280, b*2)], fill='#FFFFFF')
        draw.rectangle([(0, 720-b*2), (1280, 720-b)], fill='#FFFFFF')
        draw.rectangle([(0, 720-b), (1280, 720)], fill='#138808')
        
        try:
            tf = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 100)
            df = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 60)
        except:
            tf = df = ImageFont.load_default()
        
        t = "Daily Current Affairs"
        tb = draw.textbbox((0, 0), t, font=tf)
        tx = (1280 - (tb[2] - tb[0])) // 2
        draw.text((tx+4, 284), t, font=tf, fill=(0, 0, 0))
        draw.text((tx, 280), t, font=tf, fill=(255, 255, 255))
        
        d = datetime.strptime(date_str, '%Y-%m-%d').strftime('%d %B %Y')
        db = draw.textbbox((0, 0), d, font=df)
        dx = (1280 - (db[2] - db[0])) // 2
        draw.text((dx+3, 423), d, font=df, fill=(0, 0, 0))
        draw.text((dx, 420), d, font=df, fill=(255, 200, 80))
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path, quality=95)
        return output_path
    
    def split_text(self, text, max_chars=4000):
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        chunks = []
        current = ""
        
        for s in sentences:
            s = s.strip()
            if not s:
                continue
            sp = s + ". "
            if len(current) + len(sp) > max_chars:
                if current:
                    chunks.append(current.strip())
                current = sp
            else:
                current += sp
        
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
            
            # 1.25x speed = rate of 1.15 (Azure SSML limitation)
            ssml = f"""
            <speak version='1.0' xml:lang='hi-IN'>
                <voice name='hi-IN-MadhurNeural'>
                    <prosody rate='1.15' pitch='+0%'>
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
            
            result = synthesizer.speak_ssml_async(ssml).get()
            return result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted
        except:
            return False
    
    def generate_audio(self, script, output_path):
        print("\n🎙️  Generating audio (1.25x speed)...")
        
        os.makedirs("output/upsc/chunks", exist_ok=True)
        chunks = self.split_text(script, 4000)
        print(f"   Chunks: {len(chunks)}")
        
        chunk_files = []
        for i, chunk in enumerate(chunks, 1):
            cf = f"output/upsc/chunks/chunk_{i:03d}.mp3"
            print(f"   {i}/{len(chunks)}...", end=' ')
            if self.generate_audio_chunk(chunk, cf):
                chunk_files.append(cf)
                print("✓")
            else:
                print("✗")
            time.sleep(2)
        
        if not chunk_files:
            return False
        
        if len(chunk_files) == 1:
            subprocess.run(['cp', chunk_files[0], output_path], check=True)
        else:
            cl = "output/upsc/chunks/concat_list.txt"
            with open(cl, "w") as f:
                for cf in chunk_files:
                    f.write(f"file '{os.path.abspath(cf)}'\n")
            subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", cl, "-c", "copy", output_path], check=True, capture_output=True)
        
        print(f"✅ Audio: {os.path.getsize(output_path)/(1024*1024):.1f} MB")
        return True
    
    def create_video(self, audio_path, bg_path, output_path):
        print("\n🎬 Creating video...")
        subprocess.run(['ffmpeg', '-y', '-loop', '1', '-i', bg_path, '-i', audio_path, '-c:v', 'libx264', '-tune', 'stillimage', '-c:a', 'aac', '-b:a', '192k', '-pix_fmt', 'yuv420p', '-shortest', output_path], check=True, capture_output=True)
        print(f"✅ Video: {os.path.getsize(output_path)/(1024*1024):.1f} MB")
        return output_path
    
    def create_complete_video(self, script_path, date_str):
        print(f"\n{'='*70}")
        print(f"  UPSC Video - {date_str}")
        print(f"{'='*70}")
        
        with open(script_path, 'r', encoding='utf-8') as f:
            script = f.read()
        
        for d in ['audio', 'backgrounds', 'videos', 'thumbnails', 'chunks']:
            os.makedirs(f'output/upsc/{d}', exist_ok=True)
        
        ap = f'output/upsc/audio/audio_{date_str}.mp3'
        bp = f'output/upsc/backgrounds/bg_{date_str}.png'
        vp = f'output/upsc/videos/current_affairs_{date_str}.mp4'
        tp = f'output/upsc/thumbnails/thumb_{date_str}.png'
        
        if not self.generate_audio(script, ap):
            return None
        
        print("\n🖼️  Background...")
        self.get_background(bp)
        self.create_thumbnail(date_str, tp)
        self.create_video(ap, bp, vp)
        
        print(f"\n{'='*70}")
        print("  🎉 DONE!")
        print(f"{'='*70}")
        
        return {'video': vp, 'thumbnail': tp, 'audio': ap}

def main():
    date_str = datetime.now().strftime('%Y-%m-%d')
    sp = f'output/upsc/scripts/script_{date_str}.txt'
    
    if not os.path.exists(sp):
        print("❌ No script")
        return
    
    creator = UPSCVideoCreator()
    creator.create_complete_video(sp, date_str)

if __name__ == "__main__":
    main()
