# Cổng dùng trong lab
Web 8080, 
App 8085 (listen 8081 nội bộ), 
DB 3320 (listen 3306 nội bộ), 
Auth 8081, 
MinIO 9000/9001, 
DNS 1053/udp,
Prometheus 9090, 
NodeExporter 9100, 
Grafana 3000, 
Proxy 80.

# Chạy container:
docker compose build --no-cache
docker compose up -d 
docker ps

# Config Docker desktop để build
Sửa file cấu hình Docker daemon (cách tốt nhất)

Mở Docker Desktop

Vào Settings → Docker Engine

Bạn sẽ thấy nội dung JSON kiểu như:

{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  }
}

Chèn thêm dòng DNS vào, ví dụ:

{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "dns": ["8.8.8.8", "1.1.1.1"]
}

# Install dig
https://phoenixnap.com/kb/dig-windows
winget search bind
winget install ISC.Bind
Tắt hết terminal và gõ: dig -v
==> 
Power shell: dig --% @127.0.0.1 -p 1053 web-frontend-server.cloud.local +short
Bash/Command Promt: dig @127.0.0.1 -p 1053 web-frontend-server.cloud.local +short
Kết quả: 10.10.0.10

# Test DB
docker run -it --rm --network cloud-net mysql:8 \sh -lc 'mysql -h relational-database-server -uroot -proot -e "USE minicloud; SHOW TABLES; SELECT * FROM notes;"'

# Ping all bằng Powershell
$hosts = "web-frontend-server","application-backend-server","db","keycloak","minio","prometheus","grafana","internal-dns-server"

foreach ($h in $hosts) {
  Write-Host "===== Pinging $h from application-backend-server ====="
  docker exec application-backend-server ping -c 3 $h
  Write-Host ""
}
