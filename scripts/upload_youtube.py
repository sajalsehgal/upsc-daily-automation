"""
Upload UPSC video to YouTube
"""
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime

class YouTubeUploader:
    def __init__(self, client_secrets_file='config/youtube-oauth.json'):
        self.client_secrets_file = client_secrets_file
        self.scopes = ['https://www.googleapis.com/auth/youtube.upload']
        self.youtube = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with YouTube API"""
        print("🔐 Authenticating with YouTube...")
        
        credentials = None
        token_file = 'youtube-token.pickle'
        
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                credentials = pickle.load(token)
        
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, self.scopes)
                credentials = flow.run_local_server(port=8080)
            
            with open(token_file, 'wb') as token:
                pickle.dump(credentials, token)
        
        self.youtube = build('youtube', 'v3', credentials=credentials)
        print("✅ Authenticated successfully!")
    
    def upload_video(self, video_path, title, description, tags, thumbnail_path=None):
        """Upload video to YouTube"""
        print(f"\n📤 Uploading to YouTube...")
        print(f"   Title: {title[:60]}...")
        
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': '27'  # Education
            },
            'status': {
                'privacyStatus': 'public',
                'selfDeclaredMadeForKids': False
            }
        }
        
        media = MediaFileUpload(video_path, chunksize=1024*1024, resumable=True)
        
        request = self.youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"   Upload progress: {progress}%", end='\r')
        
        video_id = response['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        print(f"\n✅ Video uploaded!")
        print(f"   Video ID: {video_id}")
        print(f"   URL: {video_url}")
        
        # Upload thumbnail
        if thumbnail_path and os.path.exists(thumbnail_path):
            print(f"\n📸 Uploading thumbnail...")
            try:
                self.youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(thumbnail_path)
                ).execute()
                print("✅ Thumbnail uploaded!")
            except Exception as e:
                print(f"⚠️  Thumbnail upload failed: {e}")
        
        return video_id, video_url

def main():
    """Test upload"""
    from datetime import datetime
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    video_path = f'output/upsc/videos/current_affairs_{date_str}.mp4'
    thumb_path = f'output/upsc/thumbnails/thumb_{date_str}.png'
    
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return
    
    # YouTube metadata
    date_display = datetime.now().strftime('%d %B %Y')
    title = f"Daily Current Affairs {date_display} | UPSC & सरकारी परीक्षा | Top 10 News in Hindi"
    
    description = f"""📚 {date_display} के Top 10 Current Affairs

आज के महत्वपूर्ण समाचार जो UPSC और सभी सरकारी परीक्षाओं के लिए जरूरी हैं।

✅ UPSC Prelims & Mains के लिए relevant
✅ सरल हिंदी में explanation  
✅ हर खबर की UPSC relevance
✅ Key facts, dates और names

📌 Topics Covered:
- Government Policies & Schemes
- International Relations
- Economy & Budget
- Environment & Climate
- Science & Technology
- Social Issues
- Important Appointments
- Supreme Court Judgments

🔔 Subscribe करें और Bell Icon दबाएं!
रोज़ सुबह 7 बजे नई video

#UPSC #CurrentAffairs #Hindi #SarkariExam #IAS #UPSC2026 #DailyNews #भारतीयसमाचार #सरकारीपरीक्षा #आईएएस"""

    tags = [
        'upsc current affairs',
        'current affairs hindi',
        'daily current affairs',
        'upsc 2026',
        'sarkari exam',
        'ias preparation',
        'upsc preparation',
        'current affairs today',
        'upsc hindi',
        'government exam',
        'news analysis',
        'भारतीय समाचार'
    ]
    
    print("\n" + "="*70)
    print("  UPLOADING TO YOUTUBE")
    print("="*70)
    print(f"\nVideo: {video_path}")
    print(f"Size: {os.path.getsize(video_path)/(1024*1024):.1f} MB")
    
    response = input("\nType 'UPLOAD' to confirm: ")
    if response.strip().upper() != 'UPLOAD':
        print("❌ Upload cancelled")
        return
    
    uploader = YouTubeUploader()
    video_id, url = uploader.upload_video(
        video_path=video_path,
        title=title,
        description=description,
        tags=tags,
        thumbnail_path=thumb_path
    )
    
    print("\n" + "="*70)
    print("  🎉 SUCCESS!")
    print("="*70)
    print(f"\nWatch: {url}")
    print(f"Studio: https://studio.youtube.com/video/{video_id}/edit")
    print("="*70)

if __name__ == "__main__":
    main()
