"""Put a voice recording on demo.mp4:  python video/merge.py my_voice.m4a  ->  demo_voiced.mp4
If the voice is longer than the video, the last slide is held; if shorter, the end is silent."""
import subprocess, sys, json
a = sys.argv[1]
def dur(f): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]).strip())
v, au = dur("demo.mp4"), dur(a)
print(f"video {v:.1f}s, voice {au:.1f}s")
if au > 300: print("WARNING: voice is over 5:00, the assignment limit")
pad = max(0, au - v)
subprocess.run(["ffmpeg","-y","-v","error","-i","demo.mp4","-i",a,"-filter_complex",
  f"[0:v]tpad=stop_mode=clone:stop_duration={pad:.2f}[v];[1:a]apad,aresample=44100[a]",
  "-map","[v]","-map","[a]","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-t",f"{max(v,au):.2f}","demo_voiced.mp4"],check=True)
print("wrote demo_voiced.mp4")
