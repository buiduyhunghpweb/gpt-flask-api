from flask import Flask, request, jsonify
from supabase import create_client, Client
from rapidfuzz import process

# --- Cấu hình Supabase ---
SUPABASE_URL = "https://skrmxsdfimvelnkrnhif.supabase.co"  # Thay bằng URL thật của bạn
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNrcm14c2RmaW12ZWxua3JuaGlmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY4NjAwMDEsImV4cCI6MjA2MjQzNjAwMX0.KFBDyJ92KrDFuI8atA_tq50IsAmPlixmsaNYiAeUbq4"   # Thay bằng key thật


API_TOKEN = "ban-chon-token-gi-cung-duoc-123"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

# --- Kiểm tra token từ header hoặc query param ---

def check_auth_token():
    token = request.headers.get("Authorization", "")
    if token.startswith("Bearer "):
        token = token[7:]

    if not token:
        token = request.args.get("token", "")

    if not token and request.method == "POST":
        try:
            token = request.json.get("token", "")
        except:
            token = ""

    return token == API_TOKEN

# --- Chuẩn hóa tên dự án ---
def normalize_name(name: str) -> str:
    if not isinstance(name, str):
        return ""
    name = name.lower().replace("trạm biến áp", "tba").replace("trạm", "tba").replace(" ", "")
    return name

def find_best_project(input_text: str, project_list: list):
    norm_input = normalize_name(input_text)
    matches = []
    for p in project_list:
        raw_name = p.get("ten_du_an", "")
        if norm_input in normalize_name(raw_name):
            matches.append(p)
    if len(matches) == 1:
        return matches[0], []
    elif matches:
        return None, matches
    return None, []

# --- GET /event ---
@app.route("/event", methods=["GET"])
def get_events():
    if not check_auth_token():
        return jsonify({"error": "Không có quyền truy cập"}), 401

    du_an = request.args.get("du_an", "")
    projects = supabase.table("project").select("id, ten_du_an").execute().data
    matched_project, suggestions = find_best_project(du_an, projects)

    if not matched_project:
        return jsonify({
            "error": "Không tìm thấy dự án phù hợp",
            "suggestions": [p["ten_du_an"] for p in suggestions]
        }), 404

    events = supabase.table("events").select("*").eq("project_id", matched_project["id"]).execute().data
    return jsonify({
        "project": matched_project["ten_du_an"],
        "so_luong": len(events),
        "events": events
    })
@app.route("/query", methods=["POST"])
def query_data():
    if not check_auth_token():
        return jsonify({"error": "Không có quyền truy cập"}), 401

    try:
        data = request.json
        sql = data.get("sql", "")
        if not sql.lower().startswith("select"):
            return jsonify({"error": "Chỉ hỗ trợ truy vấn SELECT"}), 400

        result = supabase.rpc("run_custom_sql", {"query_text": sql}).execute()
        return jsonify(result.data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

