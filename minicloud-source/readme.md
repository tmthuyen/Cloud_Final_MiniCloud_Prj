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

- Thêm insert bảng notes: 
INSERT INTO notes (title, created_at) VALUES
('Final Report Testing Database', now()),
('Danh sách 3 blog', now());

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

- Vào database: 
docker run -it --rm --network cloud-net mysql:8 sh -lc 'mysql -h relational-database-server -uroot -proot <<EOF
USE studentdb;
SHOW tables;
SELECT * FROM students;
EOF
'
<!-- insert -->
docker run -it --rm --network cloud-net mysql:8 sh -lc 'mysql -h relational-database-server -uroot -proot <<EOF
USE studentdb;

INSERT INTO students(student_id, fullname, dob, major) VALUES 
("SV52300070", "Tran Minh Thuyen 70", "2005-01-07", "IT"),
("SV52300212", "Nguyen Tuan Kiet 12",  "2005-01-12", "IT"),
("SV52300213", "Nguyen Tuan Kiet 13",    "2005-01-13", "IT");

SELECT * FROM students;
EOF
'

USE studentdb;
INSERT INTO students(student_id, fullname, dob, major) VALUES 
('52300070', 'Tran Minh Thuyen', '2005-01-07', 'IT'),
('52300212', 'Nguyen Tuan Kiet',  '2005-01-12', 'IT'),
('52300213', 'Nguyen Tuan Kiet',    '2005-01-13', 'IT');

- update
docker run -it --rm --network cloud-net mysql:8 sh -lc 'mysql -h relational-database-server -uroot -proot <<EOF
USE studentdb;

UPDATE students
SET fullname = "Tran Minh Thuyen 52300070"
WHERE id = 7;

SELECT * FROM students;
EOF
' 

- delete
docker run -it --rm --network cloud-net mysql:8 sh -lc 'mysql -h relational-database-server -uroot -proot <<EOF
USE studentdb;
SELECT * FROM students;

DELETE FROM students WHERE id = 8;

SELECT * FROM students;
EOF
'  


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

TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJTczdYNnpackpCVlQ2ZzVwRkJ2UFhWOXZjc09MNXN0YnVIa21aR1N4T3prIn0.eyJleHAiOjE3NjQ2MTM0NTcsImlhdCI6MTc2NDYxMzE1NywianRpIjoib25ydHJvOjRmNTlkZmU0LTI2YzMtODM2MS1hNGY4LWMyMzE3OTVkYjQ5YSIsImlzcyI6Imh0dHA6Ly9sb2NhbGhvc3Q6ODA4MS9yZWFsbXMvcmVhbG1fNTIzMDAwNzAiLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiZmIzN2RmYjItMmQ2ZC00NDc4LTlmZmItOWYwMzAyMWExZDFiIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiZmxhc2stYXBwIiwic2lkIjoiZTY4MzBhY2YtN2VjMS04ZmQzLTdlNzQtMmY3NmY0YmE4YTNhIiwiYWNyIjoiMSIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIiwiZGVmYXVsdC1yb2xlcy1yZWFsbV81MjMwMDA3MCJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoicHJvZmlsZSBlbWFpbCIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6Ik1pbmggVGh1ecOqbiBUcuG6p24iLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiI1MjMwMDA3MCIsImdpdmVuX25hbWUiOiJNaW5oIFRodXnDqm4iLCJmYW1pbHlfbmFtZSI6IlRy4bqnbiIsImVtYWlsIjoidHJhbnRodXllbjIyMjJAZ21haWwuY29tIn0.UMP2V0ELq-djXfwSSS68Et3UEuUggVnWTNzgn0LlSxVvpYUtCURK1pehb8YBnuLSoa4UofstrE5CYsbAfBj1ASZx-__gMHNxKjENjsn1O2Fo50_mCkD0FCGEn_hk8MT2vdTd3KG3sz_7Y2WrxMjjoki1M0294tHmvG2X9o1XtC-ykPwVgoJx4ugNWA0tTSdpnmsptYTPETN1W_gWa8wXIcts3ysL8JC2FQMAQMwnXKxzf-WHVjW3YyMkyKmNkcQ0-5L5SwCXMaUqAj2I3ki6KuBW_lHmGl8Rd8xoSAEO9PXU_7BNZc3nBUKwR4hD8fqMi8527tcAcFn1-68HqKC8og"

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8085/secure

# hoặc nếu đi qua gateway:
# curl -H "Authorization: Bearer $TOKEN" http://localhost/api/secure

# Mục 6
- Power shell: 
dig --% @127.0.0.1 -p 1053 web-frontend-server.cloud.local +short
dig --% @127.0.0.1 -p 1053 app-backend.cloud.local +short
dig --% @127.0.0.1 -p 1053 minio.cloud.local +short
dig --% @127.0.0.1 -p 1053 keycloak.cloud.local +short
Bash/Command Prompt: 
dig @127.0.0.1 -p 1053 app-backend.cloud.local +short => 10.10.10.20
dig @127.0.0.1 -p 1053 minio.cloud.local +short => 10.10.10.30
dig @127.0.0.1 -p 1053 keycloak.cloud.local +short => 10.10.10.40


# Mục 9
- http://localhost/student/
- curl http://localhost/student/

# Mục 10
- curl http://localhost/

ping -n 3 web-frontend-server
ping -n 3 application-backend-server
ping -n 3 relational-database-server
ping -n 3 authentication-identity-server
ping -n 3 object-storage-server
ping -n 3 monitoring-prometheus-server
ping -n 3 monitoring-grafana-dashboard-server
ping -n 3 internal-dns-server

# build image web (Đứng tại root cửa source folder)
- docker compose build web-frontend-server web-frontend-server-2 application-backend-server
- Hoặc: docker compose build
- Kiểm tra: docker images | grep thuyenkietkiet

- Sửa tên image: docker tag thuyenkietkiet/web:dev tranthuyendocker/web:dev

- Push image vô account: docker push tranthuyendocker/web:dev

- Tên image trong docker-compose.yml (trên EC2) em có thể dùng: image: tranthuyendocker/web:dev


# Kiểm thử
1. docker compose build --no-cache
2. docker compose up -d
3. docker compose ps


# Hướng dẫn deploy
## Push image:
1. Login docker hub:
```
docker login -u <username>
```

2. Build image từ compose:
- Build:
```
docker compose build web-frontend-server web-frontend-server-2 application-backend-server
```
- Kiểm tra images:
```
docker images | grep <username>
```

3. Push images:
```
docker push <username>/myminicloud-web:dev
```
```
docker push <username>/myminicloud-web2:dev
```
```
docker push <username>/myminicloud-app:dev
```

## Tạo instance EC2
1. Tạo EC2 & mở port
- Launch EC2: Ubuntu 22.04, loại t3.micro (đang dùng).
- Security Group inbound rules:
* SSH: port 22, Source: My IP
* HTTP: port 80, Source: 0.0.0.0/0
* (Optional để test trực tiếp)
8080 (web1), 8085 (app), 8081 (Keycloak), 9001 (MinIO), 9090 (Prometheus), 3000 (Grafana)


# Truy cập instance, cài đặt docker và push source
1. Vào instance:
```
ssh -i "thuyenlab6.pem" ubuntu@ec2-13-214-220-73.ap-southeast-1.compute.amazonaws.com
```

2. Cài đặt docker trong EC2:
- Cài docker
```
cd ~
sudo apt update
sudo apt install -y ca-certificates curl gnupg

curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```
- Kiểm tra docker:
```
docker --version
docker compose version
```

3. Copy project lên EC2
```
scp -i "C:\52300070_TMTHUYEN\Nam-3\Nam-3_HK1_2526\4-Dien_toan_dam_may\Cloud_Final\Cloud-Final_Mini-Cloud-Project\minicloud-source\thuyenlab6.pem" -r . \
  ubuntu@ec2-18-142-96-215.ap-southeast-1.compute.amazonaws.com:/home/ubuntu/minicloud-source
```

4. Vào EC2
```
ssh -i "thuyenlab6.pem" ubuntu@ec2-18-142-96-215.ap-southeast-1.compute.amazonaws.com
ssh -i "thuyenlab6.pem" ubuntu@ec2-47-129-243-95.ap-southeast-1.compute.amazonaws.com
```

5. Chạy:
```
sudo docker compose up -d
```

