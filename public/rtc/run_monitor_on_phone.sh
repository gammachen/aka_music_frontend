curl -X POST -H "Content-Type: application/json" -d '{"server_url":"http://your-server/upload"}' http://localhost:5000/capture

curl -X POST -H "Content-Type: application/json" -d '{"server_url":"http://192.168.31.150:5005/upload"}' http://192.168.31.81:5003/capture

curl -X POST -H "Content-Type: application/json" -d '{}' http://192.168.31.81:5003/capture