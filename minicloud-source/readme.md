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


# Ping all bằng Powershell
$hosts = "web-frontend-server","application-backend-server","db","keycloak","minio","prometheus","grafana","internal-dns-server"

foreach ($h in $hosts) {
  Write-Host "===== Pinging $h from application-backend-server ====="
  docker exec application-backend-server ping -c 3 $h
  Write-Host ""
}

# Mục 1: Web Frontend Server


# Mục 2: Application Backend Server
- http://localhost:8085/hello
- http://localhost/api/hello
- http://localhost/student
- http://localhost/api/students-db

# Mục 3: relational-database
- Test DB trong git Bash
docker run -it --rm --network cloud-net mysql:8 \sh -lc 'mysql -h relational-database-server -uroot -proot -e "USE minicloud; SHOW TABLES; SELECT * FROM notes;"'

- Tạo mới studentdb
docker run -it --rm --network cloud-net mysql:8 sh -lc \
'mysql -h relational-database-server -uroot -proot'
CREATE DATABASE IF NOT EXISTS studentdb;
USE studentdb;

CREATE TABLE students (
  id INT PRIMARY KEY AUTO_INCREMENT,
  student_id VARCHAR(10),
  fullname VARCHAR(100),
  dob DATE,
  major VARCHAR(50)
);

INSERT INTO students (student_id, fullname, dob, major) VALUES
('SV001', 'Nguyen Van A', '2002-05-10', 'IT'),
('SV002', 'Tran Thi B',  '2003-01-20', 'Business'),
('SV003', 'Le Van C',    '2001-12-01', 'Communication');

SELECT * FROM students;

- Vào database
docker run -it --rm --network cloud-net mysql:8 sh -lc 'mysql -h relational-database-server -uroot -proot'
<!-- Chọn database và table students -->
USE studentdb;
SHOW tables;
SELECT * FROM students;
<!-- insert -->
USE studentdb;
INSERT INTO students(student_id, fullname, dob, major) VALUES 
('52300070', 'Tran Minh Thuyen', '2005-01-07', 'IT'),
('52300212', 'Nguyen Tuan Kiet',  '2005-01-12', 'IT'),
('52300213', 'Nguyen Tuan Kiet',    '2005-01-13', 'IT');

- update
UPDATE students
SET student_id = '523000X1'
WHERE id = 1;

- delete
DELETE FROM students WHERE id = 2; SELECT * FROM students;


# Mục 4: Authentication Identity Server
- http://localhost:8081

lấy token
curl --request POST \
  --url http://localhost:8081/realms/realm_52300070/protocol/openid-connect/token \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data 'grant_type=password' \
  --data 'client_id=flask-app' \
  --data 'username=52300070' \
  --data 'password=123456'

TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJTczdYNnpackpCVlQ2ZzVwRkJ2UFhWOXZjc09MNXN0YnVIa21aR1N4T3prIn0.eyJleHAiOjE3NjM2NjIyNjQsImlhdCI6MTc2MzY2MTk2NCwianRpIjoib25ydHJvOmEyMjQ5Y2MwLWY5MTEtY2YwNy1mYTI3LTJmOTVmNzNlYTMyOSIsImlzcyI6Imh0dHA6Ly9sb2NhbGhvc3Q6ODA4MS9yZWFsbXMvcmVhbG1fNTIzMDAwNzAiLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiZmIzN2RmYjItMmQ2ZC00NDc4LTlmZmItOWYwMzAyMWExZDFiIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiZmxhc2stYXBwIiwic2lkIjoiNGE4YzU1ZTktNDA0My0xMzE1LWYyZjQtZDNlZDQ2MzZmMTY2IiwiYWNyIjoiMSIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIiwiZGVmYXVsdC1yb2xlcy1yZWFsbV81MjMwMDA3MCJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoicHJvZmlsZSBlbWFpbCIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6Ik1pbmggVGh1ecOqbiBUcuG6p24iLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiI1MjMwMDA3MCIsImdpdmVuX25hbWUiOiJNaW5oIFRodXnDqm4iLCJmYW1pbHlfbmFtZSI6IlRy4bqnbiIsImVtYWlsIjoidHJhbnRodXllbjIyMjJAZ21haWwuY29tIn0.P39zbYgyPy11ubrYHlDYZxM1YAHOstt2YkFB-S0rAU-hmgbS1pQ-uRc_0Y20lk61RepxD_RsTS2JSTofB5yPeueewh-2fKg9Sw2WNarETdiP-qw2WYc7VgsfhlGsNLJGwi1cNw349abKQD57zFvHz-d9SoRSL6YTUe8ivGmt22oprFathBNkc5h6u0zPL4UnNIrIvD2BtrtIN9IxIDL-X0eePCqFUMH4ItP8DzO8s_jeEI0GiQv4EBBS9DBcdbtHCMY4GcTWuEjrwG4ZNKMgoCeg4AGnsd4ByD19aVIZp3kwfJazwKFT95zWJMvmPcy6PRvLmktIi6RJ9MzIquhgBg"
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8085/secure
# hoặc nếu đi qua gateway:
# curl -H "Authorization: Bearer $TOKEN" http://localhost/api/secure

# Mục 6
- Power shell: 
dig --% @127.0.0.1 -p 1053 web-frontend-server.cloud.local +short
Bash/Command Prompt: 
dig @127.0.0.1 -p 1053 application-backend.cloud.local +short => 10.10.10.20
dig @127.0.0.1 -p 1053 minio.cloud.local +short => 10.10.10.30
dig @127.0.0.1 -p 1053 keycloak.cloud.local +short => 10.10.10.40


# Mục 9
- http://localhost/student/
- curl http://localhost/student/

# Mục 10
- curl http://localhost/
