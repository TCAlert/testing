import os 
import cv2 
import subprocess

image_folder = r"C:\Users\deela\Downloads\pulsezoom2\\"
video_name = r"C:\Users\deela\Downloads\melissa12zto18z_2.mp4"

images = sorted([img for img in os.listdir(image_folder) if img.endswith((".jpg", ".jpeg", ".png"))], key=lambda x: int(os.path.splitext(x)[0]))
# images = sorted(
#     [img for img in os.listdir(image_folder) if img.endswith((".jpg", ".jpeg", ".png"))],
#     key=lambda x: int(os.path.splitext(x)[0].split('_')[1])
# )
print("Images:", images)

# Set frame from the first image
frame = cv2.imread(os.path.join(image_folder, images[0]))
height, width, layers = frame.shape
print(height, width)
newWidth, newHeight = width, height
frame = cv2.resize(frame, (newWidth, newHeight))
print(newHeight, newWidth)

# Video writer to create .avi file
video = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'mp4v'), 15, (newWidth, newHeight))

# Appending images to video
for image in images:
    f = cv2.imread(os.path.join(image_folder, image))
    f = cv2.resize(f, (newWidth, newHeight))
    video.write(f)
    
# Release the video file
video.release()
print("Video generated successfully!")


def compress_video(infile, outfile, crf=25):
    cmd = [
        'ffmpeg', '-y', '-i', infile,
        '-vcodec', 'libx264',
        '-crf', str(crf),
        outfile
    ]
    subprocess.run(cmd)

compress_video(r"C:\Users\deela\Downloads\melissa12zto18z_2.mp4", r"C:\Users\deela\Downloads\melissa12zto18z_2small.mp4", crf=25)
print('compression complete')