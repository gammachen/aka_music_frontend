
#!/bin/bash

# 创建输出目录（如果不存在）
mkdir -p dashdata

ffmpeg -i $HOME/Code/cursor-projects/aka_music/backend/app/static/def/jieba_haogui.mp4 \
  -map 0:v -map 0:v -map 0:a \
  -c:v:0 libx264 -profile:v:0 high -preset:v:0 slower -crf:v:0 22 \
  -b:v:0 3000k -maxrate:v:0 3000k -bufsize:v:0 6000k \
  -filter:v:0 "scale=1280:720:force_original_aspect_ratio=decrease,setsar=1" \
  -x264-params:v:0 "keyint=120:min-keyint=120:level=4.0" \
  -metadata:s:v:0 width=1280 -metadata:s:v:0 height=720 \
  -metadata:s:v:0 bandwidth=3000000 \
  -c:v:1 libx264 -profile:v:1 main -preset:v:1 medium -crf:v:1 24 \
  -b:v:1 1500k -maxrate:v:1 1500k -bufsize:v:1 3000k \
  -filter:v:1 "scale=854:480:force_original_aspect_ratio=decrease,setsar=1" \
  -x264-params:v:1 "keyint=120:min-keyint=120:level=3.1" \
  -metadata:s:v:1 width=854 -metadata:s:v:1 height=480 \
  -metadata:s:v:1 bandwidth=1500000 \
  -c:a aac -b:a 128k \
  -f dash \
  -seg_duration 4 \
  -adaptation_sets "id=0,streams=0,1 id=1,streams=2" \
  -use_template 1 \
  -use_timeline 1 \
  dashdata/testhaogui_high.mpd