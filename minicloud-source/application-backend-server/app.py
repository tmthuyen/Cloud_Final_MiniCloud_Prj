from flask import Flask, jsonify, request
import time, requests, os
import json
import pymysql
from jose import jwt


# ISSUER = os.getenv("OIDC_ISSUER", "http://authentication-identityserver:8080/realms/realm_52300070")
# AUDIENCE = os.getenv("OIDC_AUDIENCE", "account")
# print("Using OIDC ISSUER:", ISSUER)
ISSUER = "http://localhost:8081/realms/realm_52300070"
AUDIENCE = "account"
JWKS_URL = "http://authentication-identity-server:8080/realms/realm_52300070/protocol/openid-connect/certs"

_JWKS = None
_TS = 0

def get_jwks():
    global _JWKS, _TS
    now = time.time()
    if (not _JWKS) or (now - _TS > 600):
        resp = requests.get(JWKS_URL, timeout=5)
        resp.raise_for_status()
        _JWKS = resp.json()
        _TS = now
    return _JWKS

def get_signing_key(token: str):
    """Lấy public key từ JWKS tương ứng với kid trong token."""
    jwks = get_jwks()
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")

    for key in jwks["keys"]:
        if key.get("kid") == kid:
            # Chuyển key JSON thành public key (PEM) cho PyJWT
             # Trả về nguyên JWK dict cho jose dùng
            return key

    raise Exception("No matching JWK found for kid: " + str(kid))



# ---- Hàm tạo kết nối DB ----
def get_db_connection():
    conn = pymysql.connect(
        host="relational-database-server",  # đúng tên service trong docker-compose
        user="root",
        password="root",
        database="studentdb",
        cursorclass=pymysql.cursors.DictCursor,  # trả về dict để jsonify dễ
        charset="utf8mb4"
    )
    return conn

app = Flask(__name__)

@app.get("/hello")
def hello():
  return jsonify(message="Hello from App Server!")

@app.get("/secure")
def secure():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify(error="Missing Bearer token"), 401

    token = auth.split(" ", 1)[1]

    try:
        public_key = get_signing_key(token)
        payload = jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],
            audience=AUDIENCE,
            issuer=ISSUER,
        )
        return jsonify(
            message="Secure resource OK",
            preferred_username=payload.get("preferred_username"),
        )
    except Exception as e:
        # In ra log để debug
        print("JWT error:", repr(e))
        return jsonify(error=str(e)), 401
  
@app.get("/student")
def students():
    with open("students.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    response = {'success': True, 'message': "Students data loaded successfully", 'data': data}
    return jsonify(response)

@app.get("/students-db")
def students_db():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM students
            """)
            rows = cursor.fetchall()   # rows là list[dict]
        return jsonify(rows)
    except Exception as e:
        # Log/Báo lỗi đơn giản cho dễ debug
        print("DB error:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# get student by id
@app.get("/students-db/<string:student_id>")
def student_by_id(student_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM students WHERE student_id = %s
            """, (student_id,))
            row = cursor.fetchone()   # row là dict hoặc None
        if row:
            return jsonify(row)
        else:
            return jsonify({"error": "Student not found"}), 404
    except Exception as e:
        print("DB error:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8081)
