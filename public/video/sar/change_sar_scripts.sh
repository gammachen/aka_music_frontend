```shell

ffmpeg -i sun_yan_zhi_mv.mp4 -vf "setsar=2/1" sun_yan_zhi_mv_sar_sar_2_1.mp4

ffmpeg -i sun_yan_zhi_mv.mp4 -vf "setsar=1/2" sun_yan_zhi_mv_sar_sar_1_2.mp4

(base) shhaofu@shhaofudeMacBook-Pro mv % ffprobe -v error -select_streams v:0 -show_entries stream=sample_aspect_ratio,display_aspect_ratio sun_yan_zhi_mv_sar_sar_2_1.mp4

[STREAM]
sample_aspect_ratio=2:1
display_aspect_ratio=32:9
[/STREAM]
(base) shhaofu@shhaofudeMacBook-Pro mv % ffprobe -v error -select_streams v:0 -show_entries stream=sample_aspect_ratio,display_aspect_ratio sun_yan_zhi_mv_sar_sar_1_2.mp4

[STREAM]
sample_aspect_ratio=1:2
display_aspect_ratio=8:9
[/STREAM]
(base) shhaofu@shhaofudeMacBook-Pro mv % ffmpeg -i sun_yan_zhi_mv.mp4 -vf "setsar=1:10, setdar=16:9" sun_yan_zhi_mv_sar_sar_1_10_dar_16_9.mp4
(base) shhaofu@shhaofudeMacBook-Pro mv % ffprobe -v error -select_streams v:0 -show_entries stream=sample_aspect_ratio,display_aspect_ratio sun_yan_zhi_mv.mp4
[STREAM]
sample_aspect_ratio=1:1
display_aspect_ratio=16:9
[/STREAM]

```




