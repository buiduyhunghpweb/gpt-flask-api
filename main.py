from flask import Flask, request, jsonify
from supabase import create_client, Client
from rapidfuzz import process

# Gán trực tiếp thông tin Supabase
SUPABASE_URL ="https://skrmxsdfimvelnkrnhif.supabase.co" 
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNrcm14c2RmaW12ZWxua3JuaGlmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY4NjAwMDEsImV4cCI6MjA2MjQzNjAwMX0.KFBDyJ92KrDFuI8atA_tq50IsAmPlixmsaNYiAeUbq4"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app = Flask(__name__)

# Hàm chuẩn hóa tên
def normalize_name(name: str) -> str:
    name = name.lower()
    name = name.replace("trạm biến áp", "tba")
    name = name.replace("trạm", "tba")
    name = name.replace(" ", "")
    name = name.replace("220 kv", "220kv")
    name = name.replace("500 kv", "500kv")
    name = name.replace("-", "")
    return name

# Tìm tên dự án gần nhất
def find_best_project(input_text: str, project_list: list):
    norm_input = normalize_name(input_text)
    norm_names = [normalize_name(p['ten_du_an']) for p in project_list]
    result = process.extractOne(norm_input, norm_names)
    if result and result[1] > 80:
        index = norm_names.index(result[0])
        return project_list[index]
    return None

# === API: Thêm event mới ===
@app.route("/event", methods=["POST"])
def add_event():
    data = request.json
    short_name = data.get("du_an")
    projects = supabase.table("projects").select("*").execute().data
    matched_project = find_best_project(short_name, projects)
    if not matched_project:
        return jsonify({"error": "Không tìm thấy dự án phù hợp"}), 404

    event_data = {
        "project_id": matched_project["id"],
        "ngay_van_ban": data.get("ngay_van_ban"),
        "so_van_ban": data.get("so_van_ban"),
        "noi_dung_tom_tat": data.get("noi_dung_tom_tat"),
        "noi_dung_day_du": data.get("noi_dung_day_du"),
        "ghi_chu": data.get("ghi_chu"),
        "nguoi_thuc_hien": data.get("nguoi_thuc_hien"),
        "tinh_trang": data.get("tinh_trang"),
    }
    supabase.table("events").insert(event_data).execute()
    return jsonify({"success": True, "project": matched_project["ten_du_an"]})

# === API: Lấy danh sách event theo dự án ===
@app.route("/event", methods=["GET"])
def list_events():
    short_name = request.args.get("du_an")
    if not short_name:
        return jsonify({"error": "Thiếu tham số 'du_an'"}), 400

    projects = supabase.table("projects").select("*").execute().data
    matched_project = find_best_project(short_name, projects)
    if not matched_project:
        return jsonify({"error": "Không tìm thấy dự án phù hợp"}), 404

    events = supabase.table("events").select("*").eq("project_id", matched_project["id"]).execute().data
    return jsonify({
        "project": matched_project["ten_du_an"],
        "so_luong": len(events),
        "events": events
    })

# === Local test ===
if __name__ == "__main__":
    app.run(debug=True)
