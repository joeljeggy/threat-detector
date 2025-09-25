from google import genai
from google.genai import types
from pydantic import BaseModel
import subprocess
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

class Output(BaseModel):
    action: str
    threat_rating: int
    discription: str

gemini_api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=gemini_api_key)

video_file_name = "threat3.mp4"
compressed_file = "small_"+video_file_name
video_bytes = open(video_file_name, 'rb').read()

response = client.models.generate_content(
    model='models/gemini-2.5-pro',
    contents=types.Content(
        parts=[
            types.Part(
                inline_data=types.Blob(data=video_bytes, mime_type='video/mp4'),
                video_metadata=types.VideoMetadata(mediaResolution='MEDIA_RESOLUTION_LOW')
            ),
            types.Part(text='this is a cctv visual from my house\'s front door,explain what is happening in the video,rate the video for threat out of ten,if there is a threat describe what it is doing there.')
        ]
    ),
    config={
        "response_mime_type": "application/json",
        "response_schema": Output,
    },
)
print(response.text)
print(response.usage_metadata)

response_text = response.text
data = json.loads(response_text)

webhook_url = 'https://discord.com/api/webhooks/1391033437690794024/SyIEJR0bA5cBRZAiLB8t9f3xyXwRMlH1xV41-udSHe30bgWeud_OtwsS2zp9rFgcDIaZ'

subprocess.run([
    "ffmpeg", "-i", video_file_name, "-vcodec", "libx264", "-crf", "28", compressed_file
])

with open(compressed_file, 'rb') as f:
    files = {
        'file': (compressed_file, f, 'video/mp4')
    }
    data = {
        'content':"@everyone Intruder Alert!\n"+data["action"] if data["threat_rating"]>5 else "someone at the door!\n"+data["action"]
    }

    response = requests.post(webhook_url, data=data, files=files)

if response.ok:
    print("Video sent successfully!")
    
else:
    print(response.status_code, response.text)

os.remove(compressed_file)