"""
Auto-upload UPSC video to YouTube (for GitHub Actions)
"""
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime

# Same as upload_youtube.py but without confirmation prompt

class YouTubeUploader:
    def __init__(self, client_secrets_file='config/youtube-oauth.json'):
        self.client_secrets_file = client_secrets_file
        self.scopes = ['https://www.googleapis.com/auth/youtube.upload']
        self.youtube = None
        self.authenticate()
    
    def authenticate(self):
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
                raise Exception("No valid credentials - run manual upload first!")
        
        self.youtube = build('youtube', 'v3', credentials=credentials)
        print("✅ Authenticated!")
    
    def upload_video(self, video_path, title, description, tags, thumbnail_path=None):
        print(f"\n📤 Uploading to YouTube...")
        
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': '27'
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
                print(f"   Progress: {progress}%", end='\r')
        
        video_id = response['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        print(f"\n✅ Uploaded: {video_url}")
        
        if thumbnail_path and os.path.exists(thumbnail_path):
            print(f"📸 Uploading thumbnail...")
            try:
                self.youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(thumbnail_path)
                ).execute()
                print("✅ Thumbnail uploaded!")
            except Exception as e:
                print(f"⚠️ Thumbnail failed: {e}")
        
        return video_id, video_url

def main():
    date_str = datetime.now().strftime('%Y-%m-%d')
    video_path = f'output/upsc/videos/current_affairs_{date_str}.mp4'
    thumb_path = f'output/upsc/thumbnails/thumb_{date_str}.png'
    
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return
    
    date_display = datetime.now().strftime('%d %B %Y')
    title = f"Daily Current Affairs {date_display} | UPSC & सरकारी परीक्षा | Top 10 News in Hindi"
    
    description = f"""📚 {date_display} के Top 10 Current Affairs

✅ UPSC Prelims & Mains के लिए relevant
✅ सरल हिंदी में explanation
✅ Key facts और UPSC relevance

🔔 Subscribe करें!

#UPSC #CurrentAffairs #Hindi"""

    tags = ['upsc', 'current affairs', 'hindi', 'upsc 2026', 'sarkari exam']
    
    uploader = YouTubeUploader()
    video_id, url = uploader.upload_video(video_path, title, description, tags, thumb_path)
    
    print(f"\n🎉 SUCCESS: {url}")

if __name__ == "__main__":
    main()
