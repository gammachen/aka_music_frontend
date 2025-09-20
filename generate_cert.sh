#!/bin/bash

# 创建证书目录
mkdir -p certs

# 生成自签名证书，支持localhost和alphago.ltd
openssl req -x509 -newkey rsa:4096 -nodes -out certs/cert.pem -keyout certs/key.pem -days 365 -subj "/CN=localhost" -config <(cat <<EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
CN = localhost

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = alphago.ltd
DNS.3 = *.alphago.ltd
IP.1 = 127.0.0.1
EOF) -extensions v3_req

echo "自签名证书已生成在 certs 目录下"
echo "cert.pem - 证书文件"
echo "key.pem - 私钥文件"