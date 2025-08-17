from flask import Flask, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

# Thông tin kết nối Supabase
url = "https://skrmxsdfimvelnkrnhif.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNrcm14c2RmaW12ZWxua3JuaGlmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0Njg2MDAwMSwiZXhwIjoyMDYyNDM2MDAxfQ.jYZ8YjJHPRFRWbrQc0phajHLxByeu773bD15B0dx2y4"

supabase: Client = create_client(url, key)

def query_data(sql_raw: str):
    try:
        sql = sql_raw.strip().lower()

        # Chặn các truy vấn nguy hiểm
        blacklist = ["delete", "drop", "alter", "truncate"]
        if any(sql.startswith(cmd) for cmd in blacklist):
            return {"error": "Lệnh không được phép"}, 400

        # Chỉ cho phép select, insert, update
        allowed = ["select", "insert", "update"]
        if not any(sql.startswith(cmd) for cmd in allowed):
            return {"error": "Chỉ hỗ trợ SELECT, INSERT, UPDATE"}, 400

        # Gọi Supabase RPC
        result = supabase.rpc("run_custom_sql", {"query_text": sql_raw}).execute()
        print("RAW RESULT:", result)

        if result.data is None:
            return {"result": []}, 200

        return {"result": result.data}, 200

    except Exception as e:
        return {"error": str(e)}, 500

# Route Flask để nhận truy vấn SQL
@app.route("/query", methods=["POST"])
def handle_query():
    try:
        data = request.json
        sql_raw = data.get("sql", "")
        response, status = query_data(sql_raw)
        return jsonify(response), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Safe wrapper endpoint: lấy sự kiện theo tên dự án (POST, không cần SQL trực tiếp)
@app.route("/events/by-project", methods=["POST"])
def events_by_project():
    try:
        data = request.json
        project_name = data.get("project", "")
        if not project_name:
            return jsonify({"error": "Thiếu tên dự án"}), 400

        sql = f"SELECT * FROM events WHERE ten_du_an ILIKE '%{project_name}%' ORDER BY ngay_van_ban DESC LIMIT 3"
        response, status = query_data(sql)
        return jsonify(response), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
