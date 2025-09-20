#!/bin/bash

# 检查证书文件是否存在，如果不存在则生成
if [ ! -f "certs/cert.pem" ] || [ ! -f "certs/key.pem" ]; then
  echo "SSL证书不存在，正在生成..."
  ./generate_cert.sh
fi

# 使用HTTPS启动开发服务器
npm run dev
