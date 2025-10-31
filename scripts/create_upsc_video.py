"""
Create UPSC current affairs video with Hindi audio and text overlays
"""
import os
import subprocess
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import time
import html
import json

load_dotenv()

class UPSCVideoCreator:
    def __init__(self):
        self.width = 1920
        self.height = 1080
        
        # Azure TTS setup for Hindi
        self.speech_key = os.getenv('AZURE_SPEECH_KEY')
        self.speech_region = os.getenv('AZURE_SPEECH_REGION')
        
        if not self.speech_key or not self.speech_region:
            raise Exception("Azure credentials not found in .env file")
        
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key,
            region=self.speech_region
        )
        
        # Use Hindi voice - Male (professional tone)
        self.speech_config.speech_synthesis_voice_name = 'hi-IN-MadhurNeural'
        self.speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )
    
    def create_thumbnail(self, date_str, output_path):
        """Create YouTube thumbnail for UPSC video"""
        # Indian tricolor background
        img = Image.new('RGB', (1280, 720), color='#FFFFFF')
        draw = ImageDraw.Draw(img)
        
        # Tricolor stripes
        draw.rectangle([(0, 0), (1280, 240)], fill='#FF9933')  # Saffron
        draw.rectangle([(0, 240), (1280, 480)], fill='#FFFFFF')  # White
        draw.rectangle([(0, 480), (1280, 720)], fill='#138808')  # Green
        
        # Ashoka Chakra (simplified)
        center_x, center_y = 640, 360
        radius = 60
        draw.ellipse(
            [(center_x - radius, center_y - radius),
             (center_x + radius, center_y + radius)],
            fill='#000080'  # Navy blue
        )
        
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 70)
            date_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 45)
        except:
            title_font = ImageFont.load_default()
            date_font = ImageFont.load_default()
        
        # Title
        title_text = "Daily Current Affairs"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (1280 - title_width) // 2
        
        draw.text((title_x, 80), title_text, font=title_font, fill=(0, 0, 0))
        
        # Date
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        date_display = date_obj.strftime('%d %B %Y')
        date_bbox = draw.textbbox((0, 0), date_display, font=date_font)
        date_width = date_bbox[2] - date_bbox[0]
        date_x = (1280 - date_width) // 2
        
        draw.text((date_x, 550), date_display, font=date_font, fill=(255, 255, 255))
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path, quality=95)
        print(f"✅ Thumbnail created: {output_path}")
        
        return output_path
    
    def split_text_into_chunks(self, text, max_chars=4000):
        """Split text into smaller chunks for Azure TTS"""
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_with_period = sentence + ". "
            
            if len(current_chunk) + len(sentence_with_period) > max_chars:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence_with_period
            else:
                current_chunk += sentence_with_period
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def generate_audio_chunk(self, text, output_path):
        """Generate audio for a single chunk"""
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
                    <prosody rate='0.92' pitch='+0%'>
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
            
            result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return True
            else:
                print(f"\nError: {result.reason}")
                if result.reason == speechsdk.ResultReason.Canceled:
                    cancellation = result.cancellation_details
                    print(f"Error details: {cancellation.error_details}")
                return False
                
        except Exception as e:
            print(f"\nException: {e}")
            return False
    
    def generate_audio(self, script, output_path):
        """Generate Hindi audio from script in chunks"""
        print("\n🎙️  Generating Hindi audio with Azure TTS...")
        print(f"   Script length: {len(script)} characters")
        
        os.makedirs("output/upsc/chunks", exist_ok=True)
        
        chunks = self.split_text_into_chunks(script, max_chars=4000)
        total_chunks = len(chunks)
        print(f"   Split into {total_chunks} chunks")
        
        chunk_files = []
        
        for i, chunk in enumerate(chunks, 1):
            chunk_file = f"output/upsc/chunks/chunk_{i:03d}.mp3"
            print(f"   Chunk {i}/{total_chunks} ({len(chunk)} chars)...", end=' ')
            
            if not self.generate_audio_chunk(chunk, chunk_file):
                print(f"✗ Failed")
                continue
            
            chunk_files.append(chunk_file)
            print("✓")
            
            if i < total_chunks:
                time.sleep(2)
        
        if len(chunk_files) == 0:
            print("❌ No audio chunks generated!")
            return False
        
        print(f"\n   Combining {len(chunk_files)} chunks...")
        
        if len(chunk_files) == 1:
            subprocess.run(['cp', chunk_files[0], output_path], check=True)
        else:
            concat_list = "output/upsc/chunks/concat_list.txt"
            with open(concat_list, "w") as f:
                for cf in chunk_files:
                    abs_path = os.path.abspath(cf)
                    f.write(f"file '{abs_path}'\n")
            
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_list,
                "-c", "copy",
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
        
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"✅ Audio generated: {output_path} ({file_size:.1f} MB)")
        return True
    
    def create_background_with_text(self, date_str, output_path):
        """Create educational background with LARGE readable text"""
        img = Image.new('RGB', (self.width, self.height), color='#1a1a2e')
        draw = ImageDraw.Draw(img)
        
        # Gradient background
        for y in range(self.height):
            r = int(26 + (15 - 26) * (y / self.height))
            g = int(26 + (52 - 26) * (y / self.height))
            b = int(46 + (78 - 46) * (y / self.height))
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        # Tricolor border (thicker)
        border_thickness = 20
        draw.rectangle([(0, 0), (self.width, border_thickness)], fill='#FF9933')
        draw.rectangle([(0, border_thickness), (self.width, border_thickness * 2)], fill='#FFFFFF')
        draw.rectangle([(0, self.height - border_thickness * 2), (self.width, self.height - border_thickness)], fill='#FFFFFF')
        draw.rectangle([(0, self.height - border_thickness), (self.width, self.height)], fill='#138808')
        
        # Load fonts - MUCH LARGER
        try:
            # Increased font sizes significantly
            title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 140)
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 80)
            date_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 70)
        except:
            try:
                title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 140)
                subtitle_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 80)
                date_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 70)
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                date_font = ImageFont.load_default()
        
        # Main title - centered
        title_text = "Daily Current Affairs"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (self.width - title_width) // 2
        title_y = 350
        
        # Shadow for better readability
        shadow_offset = 5
        draw.text((title_x + shadow_offset, title_y + shadow_offset), title_text, font=title_font, fill=(0, 0, 0))
        # Main text
        draw.text((title_x, title_y), title_text, font=title_font, fill=(255, 255, 255))
        
        # Subtitle - centered
        subtitle_text = "UPSC & सरकारी परीक्षा"
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (self.width - subtitle_width) // 2
        subtitle_y = 520
        
        draw.text((subtitle_x + 3, subtitle_y + 3), subtitle_text, font=subtitle_font, fill=(0, 0, 0))
        draw.text((subtitle_x, subtitle_y), subtitle_text, font=subtitle_font, fill=(255, 200, 100))
        
        # Date - centered
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        date_display = date_obj.strftime('%d %B %Y')
        date_bbox = draw.textbbox((0, 0), date_display, font=date_font)
        date_width = date_bbox[2] - date_bbox[0]
        date_x = (self.width - date_width) // 2
        date_y = 640
        
        draw.text((date_x + 3, date_y + 3), date_display, font=date_font, fill=(0, 0, 0))
        draw.text((date_x, date_y), date_display, font=date_font, fill=(220, 220, 220))
        
        img.save(output_path, quality=95)
        print(f"✅ Background created with large readable text")
        return output_path
    
    def create_video(self, audio_path, background_path, output_path):
        """Combine audio and background into video"""
        print("\n🎬 Creating video...")
        
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', background_path,
            '-i', audio_path,
            '-c:v', 'libx264',
            '-tune', 'stillimage',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"✅ Video created: {output_path} ({file_size:.1f} MB)")
        
        return output_path
    
    def create_complete_video(self, script_path, date_str):
        """Complete video creation pipeline"""
        print(f"\n{'='*70}")
        print(f"  Creating UPSC Current Affairs Video - {date_str}")
        print(f"{'='*70}")
        
        with open(script_path, 'r', encoding='utf-8') as f:
            script = f.read()
        
        print(f"\n📄 Script length: {len(script)} characters")
        
        for dirname in ['audio', 'backgrounds', 'videos', 'thumbnails', 'chunks']:
            os.makedirs(f'output/upsc/{dirname}', exist_ok=True)
        
        audio_path = f'output/upsc/audio/audio_{date_str}.mp3'
        bg_path = f'output/upsc/backgrounds/bg_{date_str}.png'
        video_path = f'output/upsc/videos/current_affairs_{date_str}.mp4'
        thumb_path = f'output/upsc/thumbnails/thumb_{date_str}.png'
        
        if not self.generate_audio(script, audio_path):
            print("❌ Audio generation failed!")
            return None
        
        self.create_background_with_text(date_str, bg_path)
        self.create_thumbnail(date_str, thumb_path)
        self.create_video(audio_path, bg_path, video_path)
        
        print(f"\n{'='*70}")
        print("  🎉 VIDEO CREATION COMPLETE!")
        print(f"{'='*70}")
        print(f"Video: {video_path}")
        print(f"Thumbnail: {thumb_path}")
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
        print(f"❌ Script not found: {script_path}")
        print("   Run generate_upsc_script.py first!")
        return
    
    creator = UPSCVideoCreator()
    result = creator.create_complete_video(script_path, date_str)
    
    if result:
        print("\n✅ Ready to upload to YouTube!")

if __name__ == "__main__":
    main()
