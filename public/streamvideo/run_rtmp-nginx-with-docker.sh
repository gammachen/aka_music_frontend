docker run -d --name nginx-hls-4 \
  -p 1938:1935 \
  -p 8084:8080 \
  -v ./rtmp-nginx-conf/01_nginx_config_for_rtmp.conf:/etc/nginx/nginx.conf \
  -v ./dashdata:/mnt/dash \
  -v ./hlsdata:/mnt/hls \
  alqutami/rtmp-hls