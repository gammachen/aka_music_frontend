
# ffmpeg -i $HOME/Code/cursor-projects/aka_music/backend/app/static/def/jieba_haogui.mp4 \
#   # 映射同一视频源两次以生成两路输出
#   -map 0:v:0 -map 0:v:0 -map 0:a:0 \
#   # ------------------------------
#   # 视频流1（高清 1280x720）
#   -c:v:0 libx264 \
#   -b:v:0 3000k -maxrate 3000k -bufsize 6000k \
#   -vf "scale=1280:720" \          # 明确指定分辨率
#   -x264-params "keyint=120:min-keyint=120" \
#   -profile:v:0 high -preset slower \
#   -crf 22 \
#   # 元数据注入
#   -metadata:s:v:0 width=1280 -metadata:s:v:0 height=720 \
#   -metadata:s:v:0 bandwidth=3000000 \
#   # ------------------------------
#   # 视频流2（中清 854x480）
#   -c:v:1 libx264 \
#   -b:v:1 1500k -maxrate 1500k -bufsize 3000k \
#   -vf "scale=854:480" \            # 独立分辨率设置
#   -x264-params "keyint=120:min-keyint=120" \
#   -profile:v:1 main -preset medium \
#   -crf 24 \
#   # 元数据注入
#   -metadata:s:v:1 width=854 -metadata:s:v:1 height=480 \
#   -metadata:s:v:1 bandwidth=1500000 \
#   # ------------------------------
#   # 音频流
#   -c:a aac -b:a 128k \
#   # ------------------------------
#   # DASH参数
#   -f dash \
#   -seg_duration 4 \
#   -adaptation_sets "id=0,streams=0,1 id=1,streams=2" \  # 视频流0,1在同一个AdaptationSet
#   -use_template 1 \
#   -use_timeline 1 \
#     dashdata/testhaogui_high_fixed.mpd

ffmpeg -i $HOME/Code/cursor-projects/aka_music/backend/app/static/def/jieba_haogui.mp4 \
  -map 0:v:0 -map 0:v:0 -map 0:a:0 \
  -c:v:0 libx264 \
  -b:v:0 3000k -maxrate 3000k -bufsize 6000k \
  -vf "scale=1280:720" \
  -x264-params "keyint=120:min-keyint=120" \
  -profile:v:0 high -preset slower \
  -crf 22 \
  -metadata:s:v:0 width=1280 -metadata:s:v:0 height=720 \
  -metadata:s:v:0 bandwidth=3000000 \
  -c:v:1 libx264 \
  -b:v:1 1500k -maxrate 1500k -bufsize 3000k \
  -vf "scale=854:480" \
  -x264-params "keyint=120:min-keyint=120" \
  -profile:v:1 main -preset medium \
  -crf 24 \
  -metadata:s:v:1 width=854 -metadata:s:v:1 height=480 \
  -metadata:s:v:1 bandwidth=1500000 \
  -c:a aac -b:a 128k \
  -f dash \
  -seg_duration 4 \
  -adaptation_sets "id=0,streams=0,1 id=1,streams=2" \
  -use_template 1 \
  -use_timeline 1 \
    dashdata/testhaogui_high_fixed.mpd