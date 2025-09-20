# 单码率构建MPD
# 按参数生成mp4片段文件
# 生成MPD文件
ffmpeg -i $HOME/Code/cursor-projects/aka_music/backend/app/static/def/jieba_haogui.mp4 \
     -c:v libx264 -b:v 3M -g 60 -keyint_min 60 \
    -c:a aac -b:a 128k \
    -f dash \
    -seg_duration 4 \
    -use_template 1 \
    -use_timeline 1 \
    -init_seg_name init-\$RepresentationID\$.mp4 \
    -media_seg_name chunk-\$RepresentationID\$-\$Number%05d\$.mp4 \
     dashdata/testhaogui.mpd

# (translate-env) (base) shhaofu@shhaofudeMacBook-Pro streamvideo % tree -
# h dashdata 
# [1.6K]  dashdata
# ├── [1.8M]  chunk-0-00001.mp4
# ├── [1.9M]  chunk-0-00002.mp4
# ├── [1.7M]  chunk-0-00003.mp4
# ├── [1.6M]  chunk-0-00004.mp4
# ├── [1.8M]  chunk-0-00005.mp4
# ├── [1.4M]  chunk-0-00006.mp4
# ├── [2.3M]  chunk-0-00007.mp4
# ├── [1.6M]  chunk-0-00008.mp4
# ├── [475K]  chunk-0-00009.mp4
# ├── [ 66K]  chunk-1-00001.mp4
# ├── [ 64K]  chunk-1-00002.mp4
# ├── [ 65K]  chunk-1-00003.mp4
# ├── [ 65K]  chunk-1-00004.mp4
# ├── [ 65K]  chunk-1-00005.mp4
# ├── [ 64K]  chunk-1-00006.mp4
# ├── [ 66K]  chunk-1-00007.mp4
# ├── [ 64K]  chunk-1-00008.mp4
# ├── [ 65K]  chunk-1-00009.mp4
# ├── [ 64K]  chunk-1-00010.mp4
# ├── [ 65K]  chunk-1-00011.mp4
# ├── [7.3K]  chunk-1-00012.mp4
# ├── [ 29K]  chunk-hB%05d$.mp4
# ├── [486K]  chunk-stream0-00001.m4s
# ├── [493K]  chunk-stream0-00002.m4s
# ├── [469K]  chunk-stream0-00003.m4s
# ├── [427K]  chunk-stream0-00004.m4s
# ├── [468K]  chunk-stream0-00005.m4s
# ├── [368K]  chunk-stream0-00006.m4s
# ├── [702K]  chunk-stream0-00007.m4s
# ├── [378K]  chunk-stream0-00008.m4s
# ├── [131K]  chunk-stream0-00009.m4s
# ├── [ 66K]  chunk-stream1-00001.m4s
# ├── [ 64K]  chunk-stream1-00002.m4s
# ├── [ 65K]  chunk-stream1-00003.m4s
# ├── [ 65K]  chunk-stream1-00004.m4s
# ├── [ 65K]  chunk-stream1-00005.m4s
# ├── [ 64K]  chunk-stream1-00006.m4s
# ├── [ 66K]  chunk-stream1-00007.m4s
# ├── [ 64K]  chunk-stream1-00008.m4s
# ├── [ 65K]  chunk-stream1-00009.m4s
# ├── [ 64K]  chunk-stream1-00010.m4s
# ├── [ 65K]  chunk-stream1-00011.m4s
# ├── [7.3K]  chunk-stream1-00012.m4s
# ├── [ 857]  init-$.mp4
# ├── [ 857]  init-0.mp4
# ├── [ 764]  init-1.mp4
# ├── [ 857]  init-stream0.m4s
# ├── [ 764]  init-stream1.m4s
# ├── [2.0K]  testhaogui.mpd
# └── [2.1K]  testhaogui_selfadapter.mpd