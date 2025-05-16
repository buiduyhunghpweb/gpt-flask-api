from flask import Flask, request, jsonify
from supabase import create_client, Client
from rapidfuzz import process

# --- Cấu hình Supabase ---
SUPABASE_URL = "https://skrmxsdfimvelnkrnhif.supabase.co"  # Thay bằng URL thật của bạn
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNrcm14c2RmaW12ZWxua3JuaGlmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY4NjAwMDEsImV4cCI6MjA2MjQzNjAwMX0.KFBDyJ92KrDFuI8atA_tq50IsAmPlixmsaNYiAeUbq4"   # Thay bằng key thật

API_TOKEN = "ban-chon-token-gi-cung-duoc-123"  # Thay bằng token bí mật bạn chọn

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app = Flask(__name__)

# --- Hàm kiểm tra token ---
def check_auth_token():
    auth_header = request.headers.get("Authorization", "")
    return auth_header.startswith("Bearer ") and auth_header[7:] == API_TOKEN

# --- Chuẩn hóa tên dự án ---
def normalize_name(name: str) -> str:
    if not isinstance(name, str):
        return ""
    name = name.lower()
    name = name.replace("trạm biến áp", "tba")
    name = name.replace("trạm", "tba")
    name = name.replace(" ", "")
    return name

# --- Tìm dự án phù hợp hoặc gợi ý ---
def find_best_project(input_text: str, project_list: list):
    norm_input = normalize_name(input_text)
    matches = []

    for p in project_list:
        raw_name = p.get("ten_du_an")
        if not raw_name:
            continue

        norm_db_name = normalize_name(raw_name)
        if norm_input in norm_db_name:
            matches.append(p)

    if len(matches) == 1:
        return matches[0], []
    elif len(matches) > 1:
        return None, matches
    else:
        return None, []

# --- API POST: Thêm sự kiện ---
@app.route("/event", methods=["POST"])
def add_event():
    if not check_auth_token():
        return jsonify({"error": "Không có quyền truy cập"}), 401

    data = request.json
    short_name = data.get("du_an")
    projects = supabase.table("project").select("id, ten_du_an").execute().data
    matched_project, suggestions = find_best_project(short_name, projects)

    if not matched_project:
        return jsonify({
            "error": "Không tìm thấy dự án phù hợp",
            "suggestions": [p["ten_du_an"] for p in suggestions]
        }), 404

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

# --- API GET: Lấy danh sách sự kiện ---
@app.route("/event", methods=["GET"])
def list_events():
    if not check_auth_token():
        return jsonify({"error": "Không có quyền truy cập"}), 401

    short_name = request.args.get("du_an")
    projects = supabase.table("project").select("id, ten_du_an").execute().data
    matched_project, suggestions = find_best_project(short_name, projects)

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

# --- API POST: Thêm dự án ---
@app.route("/project", methods=["POST"])
def add_project():
    if not check_auth_token():
        return jsonify({"error": "Không có quyền truy cập"}), 401

    try:
        data = request.json
        ten_du_an = data.get("ten_du_an")
        if not ten_du_an:
            return jsonify({"error": "Thiếu trường 'ten_du_an'"}), 400

        project_data = {
            "ten_du_an": ten_du_an,
            "cong_suat_mva": data.get("cong_suat_mva"),
            "chieu_dai_km": data.get("chieu_dai_km"),
            "don_vi_quan_ly": data.get("don_vi_quan_ly"),
            "so_van_ban_giao_nhiem_vu": data.get("so_van_ban_giao_nhiem_vu"),
            "ngay_van_ban_giao_nhiem_vu": data.get("ngay_van_ban_giao_nhiem_vu"),
            "khoi_cong": data.get("khoi_cong"),
            "hoan_thanh_dong_dien": data.get("hoan_thanh_dong_dien")
        }

        supabase.table("project").insert(project_data).execute()
        return jsonify({"success": True, "ten_du_an": ten_du_an}), 200

    except Exception as e:
        return jsonify({"error": "Lỗi máy chủ", "chi_tiet": str(e)}), 500

# --- API POST: Cập nhật dự án ---
@app.route("/update-project", methods=["POST"])
def update_project():
    if not check_auth_token():
        return jsonify({"error": "Không có quyền truy cập"}), 401

    try:
        data = request.json
        ten_du_an = data.get("ten_du_an")
        if not ten_du_an:
            return jsonify({"error": "Thiếu trường 'ten_du_an'"}), 400

        projects = supabase.table("project").select("id, ten_du_an").execute().data
        matched_project, suggestions = find_best_project(ten_du_an, projects)

        if not matched_project:
            return jsonify({
                "error": "Không tìm thấy dự án phù hợp",
                "suggestions": [p["ten_du_an"] for p in suggestions]
            }), 404

        update_data = {k: v for k, v in data.items() if k != "ten_du_an"}
        supabase.table("project").update(update_data).eq("id", matched_project["id"]).execute()

        return jsonify({"success": True, "ten_du_an": matched_project["ten_du_an"]}), 200

    except Exception as e:
        return jsonify({"error": "Lỗi cập nhật", "chi_tiet": str(e)}), 500

# --- API POST: Truy vấn SQL ---
@app.route("/query", methods=["POST"])
def query_data():
    if not check_auth_token():
        return jsonify({"error": "Không có quyền truy cập"}), 401

    try:
        data = request.json
        sql = data.get("sql")

        if not sql or not sql.strip().lower().startswith("select"):
            return jsonify({"error": "Chỉ cho phép truy vấn SELECT"}), 400

        result = supabase.rpc("run_custom_sql", {"query_text": sql}).execute()
        return jsonify(result.data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Chạy local ---
if __name__ == "__main__":
    app.run(debug=True)

