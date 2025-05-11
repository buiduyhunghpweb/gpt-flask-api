from flask import Flask, request, jsonify
from supabase import create_client, Client
from rapidfuzz import process

# --- Cấu hình Supabase ---
SUPABASE_URL = "https://skrmxsdfimvelnkrnhif.supabase.co"  # Thay bằng URL thật của bạn
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNrcm14c2RmaW12ZWxua3JuaGlmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY4NjAwMDEsImV4cCI6MjA2MjQzNjAwMX0.KFBDyJ92KrDFuI8atA_tq50IsAmPlixmsaNYiAeUbq4"   # Thay bằng key thật

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app = Flask(__name__)

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
    suggestions = []
    matched_project = None

    for p in project_list:
        raw_name = p.get("ten_du_an")
        if not raw_name:
            continue
        norm_db_name = normalize_name(raw_name)

        # Khớp hoàn toàn
        if "tba" in norm_db_name and norm_input in norm_db_name:
            matched_project = p
            break

        # Gợi ý nếu có phần giống phía sau
        if "tba" in norm_db_name and norm_input[-12:] in norm_db_name:
            suggestions.append(raw_name)

    return matched_project, suggestions

# --- API POST: Thêm sự kiện ---
@app.route("/event", methods=["POST"])
def add_event():
    print("🔥 [POST] Nhận yêu cầu thêm sự kiện mới")
    data = request.json
    print("📥 Dữ liệu nhận được:", data)

    short_name = data.get("du_an")
    projects = supabase.table("project").select("id, ten_du_an").execute().data
    matched_project, suggestions = find_best_project(short_name, projects)

    if not matched_project:
        return jsonify({
            "error": "Không tìm thấy dự án phù hợp",
            "suggestions": suggestions
        }), 404

    print("✅ Dự án:", matched_project["ten_du_an"])
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
    print("✅ Đã ghi dữ liệu sự kiện vào Supabase")

    return jsonify({"success": True, "project": matched_project["ten_du_an"]})

# --- API GET: Lấy danh sách sự kiện ---
@app.route("/event", methods=["GET"])
def list_events():
    print("🔍 [GET] Nhận yêu cầu lấy danh sách sự kiện")
    short_name = request.args.get("du_an")
    print("📥 Tham số dự án:", short_name)

    projects = supabase.table("project").select("id, ten_du_an").execute().data
    matched_project, suggestions = find_best_project(short_name, projects)

    if not matched_project:
        return jsonify({
            "error": "Không tìm thấy dự án phù hợp",
            "suggestions": suggestions
        }), 404

    print("✅ Dự án:", matched_project["ten_du_an"])
    events = supabase.table("events").select("*").eq("project_id", matched_project["id"]).execute().data
    print(f"📊 Số sự kiện tìm thấy: {len(events)}")

    return jsonify({
        "project": matched_project["ten_du_an"],
        "so_luong": len(events),
        "events": events
    })

# --- Chạy local ---
if __name__ == "__main__":
    app.run(debug=True)
