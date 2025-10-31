"""
Create UPSC video with LARGE, CLEAR text
"""
import os
import subprocess
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import time
import html

load_dotenv()

class UPSCVideoCreator:
    def __init__(self):
        self.width = 1920
        self.height = 1080
        
        self.speech_key = os.getenv('AZURE_SPEECH_KEY')
        self.speech_region = os.getenv('AZURE_SPEECH_REGION')
        
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
    
    def create_thumbnail(self, date_str, output_path):
        """Create thumbnail"""
        img = Image.new('RGB', (1280, 720), color='#FFFFFF')
        draw = ImageDraw.Draw(img)
        
        # Tricolor
        draw.rectangle([(0, 0), (1280, 240)], fill='#FF9933')
        draw.rectangle([(0, 240), (1280, 480)], fill='#FFFFFF')
        draw.rectangle([(0, 480), (1280, 720)], fill='#138808')
        
        # Chakra
        center_x, center_y = 640, 360
        radius = 80
        draw.ellipse([(center_x - radius, center_y - radius),
                      (center_x + radius, center_y + radius)], fill='#000080')
        
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 90)
            date_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 55)
        except:
            title_font = ImageFont.load_default()
            date_font = ImageFont.load_default()
        
        title_text = "Daily Current Affairs"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((1280 - title_width) // 2, 80), title_text, font=title_font, fill=(0, 0, 0))
        
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        date_display = date_obj.strftime('%d %B %Y')
        date_bbox = draw.textbbox((0, 0), date_display, font=date_font)
        date_width = date_bbox[2] - date_bbox[0]
        draw.text(((1280 - date_width) // 2, 580), date_display, font=date_font, fill=(255, 255, 255))
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path, quality=95)
        print(f"✅ Thumbnail created")
        return output_path
    
    def split_text_into_chunks(self, text, max_chars=4000):
        """Split for TTS"""
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
        """Generate audio chunk"""
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
                    <prosody rate='0.90' pitch='+0%'>
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
            
            result = synthesizer.speak_ssml_async(ssml).get()
            return result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted
                
        except Exception as e:
            print(f"\nException: {e}")
            return False
    
    def generate_audio(self, script, output_path):
        """Generate audio from script"""
        print("\n🎙️  Generating audio...")
        print(f"   Script: {len(script)} chars")
        
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
    
    def create_background_with_text(self, date_str, output_path):
        """Create background with MASSIVE readable text"""
        img = Image.new('RGB', (self.width, self.height), color='#0f1729')
        draw = ImageDraw.Draw(img)
        
        # Subtle gradient
        for y in range(self.height):
            shade = int(15 + (25 - 15) * (y / self.height))
            draw.line([(0, y), (self.width, y)], fill=(shade, shade + 8, shade + 20))
        
        # Thick tricolor borders
        border = 25
        draw.rectangle([(0, 0), (self.width, border)], fill='#FF9933')
        draw.rectangle([(0, border), (self.width, border * 2)], fill='#FFFFFF')
        draw.rectangle([(0, self.height - border * 2), (self.width, self.height - border)], fill='#FFFFFF')
        draw.rectangle([(0, self.height - border), (self.width, self.height)], fill='#138808')
        
        # MASSIVE fonts
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 180)
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 100)
            date_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 80)
        except:
            try:
                title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 180)
                subtitle_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 100)
                date_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 80)
            except:
                title_font = subtitle_font = date_font = ImageFont.load_default()
        
        # Title
        title_text = "Daily Current Affairs"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_w = title_bbox[2] - title_bbox[0]
        title_x = (self.width - title_w) // 2
        title_y = 320
        
        # Heavy shadow
        draw.text((title_x + 6, title_y + 6), title_text, font=title_font, fill=(0, 0, 0))
        draw.text((title_x, title_y), title_text, font=title_font, fill=(255, 255, 255))
        
        # Subtitle
        subtitle_text = "UPSC & सरकारी परीक्षा"
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
        subtitle_w = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (self.width - subtitle_w) // 2
        subtitle_y = 540
        
        draw.text((subtitle_x + 4, subtitle_y + 4), subtitle_text, font=subtitle_font, fill=(0, 0, 0))
        draw.text((subtitle_x, subtitle_y), subtitle_text, font=subtitle_font, fill=(255, 200, 80))
        
        # Date
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        date_display = date_obj.strftime('%d %B %Y')
        date_bbox = draw.textbbox((0, 0), date_display, font=date_font)
        date_w = date_bbox[2] - date_bbox[0]
        date_x = (self.width - date_w) // 2
        date_y = 680
        
        draw.text((date_x + 3, date_y + 3), date_display, font=date_font, fill=(0, 0, 0))
        draw.text((date_x, date_y), date_display, font=date_font, fill=(230, 230, 230))
        
        img.save(output_path, quality=95)
        print(f"✅ Background with LARGE text")
        return output_path
    
    def create_video(self, audio_path, background_path, output_path):
        """Create video"""
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
        """Complete pipeline"""
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
        
        self.create_background_with_text(date_str, bg_path)
        self.create_thumbnail(date_str, thumb_path)
        self.create_video(audio_path, bg_path, video_path)
        
        print(f"\n{'='*70}")
        print("  🎉 COMPLETE!")
        print(f"{'='*70}")
        print(f"Video: {video_path}")
        print(f"Thumbnail: {thumb_path}")
        
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
    result = creator.create_complete_video(script_path, date_str)

if __name__ == "__main__":
    main()
