import requests
from bs4 import BeautifulSoup
from moviepy.editor import VideoFileClip, CompositeVideoClip
import random
from pytube import YouTube

# Making a GET request
contentSoup = ""
for i in range(random.randrange(3, 10, 1)):
    contentSoup += requests.get('https://petittube.com/').content.decode()

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(contentSoup, 'html.parser')

# Find all iframe tags and extract the src attributes
iframe_srcs = [iframe['src'] for iframe in soup.find_all('iframe')]

# Function to download video from URL with retry
def download_video(link, name):
    max_retries = 50
    for _ in range(max_retries):
        try:
            YouTube(link).streams.first().download(filename=name)
            return  # Exit the loop if download is successful
        except Exception as e:
            print(f"Error downloading video from {link}: {e}")
    
    print(f"Failed to download video from {link}")

# Load and process the first video (with sound)
first_video_url = iframe_srcs[0]
first_video_filename = ((first_video_url.replace(":","")).replace("/","")).replace(".","") + ".mp4"
download_video(first_video_url, first_video_filename)

# Load the first video with sound
first_video_clip = VideoFileClip(first_video_filename)

# Crop the first video
#first_video_clip = first_video_clip.crop(x1=0, y1=(first_video_clip.h - 780), x2=360, y2=first_video_clip.h)

# Set the duration to 15 seconds
dur = random.uniform(20, 30)
if first_video_clip.duration > dur:
    first_video_clip = first_video_clip.subclip(0, dur)
else:
    dur = first_video_clip.duration
# Create a list to store video clips for layering
video_clips = [(0, first_video_clip)]  # Start time for the first clip is 0

# Download and process the rest of the videos
for iframe_src in iframe_srcs[1:]:
    video_filename = f'{((iframe_src.replace(":","")).replace("/","")).replace(".","")}.mp4'
    download_video(iframe_src, video_filename) #remove all strings that can't be filenames

    # Load the video clip
    video_clip = VideoFileClip(video_filename)

    # Set the duration to a random value between 1 and 15 seconds
    video_duration = random.uniform(1, dur)
    if video_duration > video_clip.duration:
        video_duration = video_clip.duration
    video_clip = video_clip.subclip(0, video_duration)

    # Resize the video to a smaller size
    video_clip = video_clip.resize(width=float(first_video_clip.w)/(random.uniform(1.5, 4)))

    # Set a random position on the screen
    x_position = random.randint(0, random.randrange(1, first_video_clip.w, 1))
    y_position = random.randint(0, random.randrange(1, first_video_clip.h, 1))
    video_clip = video_clip.set_position((x_position, y_position))

    # Set a random start time for each clip
    start_time = random.uniform(0, dur - video_duration)
    video_clip = video_clip.set_start(start_time)
    video_clips.append((start_time, video_clip))

# Sort the video clips based on their start times
video_clips.sort(key=lambda x: x[0])

# Extract only the clips from the tuple
video_clips = [clip for _, clip in video_clips]

# Create a CompositeVideoClip by layering clips on top of each other
collage_clip = CompositeVideoClip(video_clips)

# Write the result to a new file
collage_clip.write_videofile('output_collage.mp4', codec='libx264', audio_codec='aac', fps=24)
