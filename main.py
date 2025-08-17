from flask import Flask, request, jsonify
from supabase import create_client, Client
from rapidfuzz import process

# --- Cấu hình Supabase ---
SUPABASE_URL = "https://skrmxsdfimvelnkrnhif.supabase.co"  # Thay bằng URL thật của bạn
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNrcm14c2RmaW12ZWxua3JuaGlmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY4NjAwMDEsImV4cCI6MjA2MjQzNjAwMX0.KFBDyJ92KrDFuI8atA_tq50IsAmPlixmsaNYiAeUbq4"   # Thay bằng key thật


API_TOKEN = "ban-chon-token-gi-cung-duoc-123"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app = Flask(__name__)
@app.route("/exec_sql", methods=["POST"])
def exec_sql():
    try:
        data = request.json or {}
        token = data.get("token", "")
        sql_raw = data.get("sql", "")

        # Kiểm tra token
        if token != API_TOKEN:
            return jsonify({"error": "Không có quyền truy cập"}), 401

        if not sql_raw:
            return jsonify({"error": "Thiếu câu lệnh SQL"}), 400

        sql = sql_raw.strip().lower()

        # Chặn lệnh nguy hiểm
        blacklist = ["delete", "drop", "alter", "truncate"]
        if any(sql.startswith(cmd) for cmd in blacklist):
            return jsonify({"error": "Lệnh không được phép"}), 400

        # Chỉ cho phép select, insert, update
        allowed = ["select", "insert", "update"]
        if not any(sql.startswith(cmd) for cmd in allowed):
            return jsonify({"error": "Chỉ hỗ trợ SELECT, INSERT, UPDATE"}), 400

        # Gọi Supabase Postgres function để thực thi SQL
        result = supabase.rpc("run_custom_sql", {"query_text": sql_raw}).execute()

        if result.data is None:
            return jsonify({"result": []}), 200

        return jsonify({"result": result.data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)



