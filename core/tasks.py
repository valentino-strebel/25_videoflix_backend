import subprocess

def convert720px(source):
    target = source + '_720p.mp4'
    cmd = 'ffmpeg -i "{}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source,target)
    subprocess.run(cmd, capture_output=True)