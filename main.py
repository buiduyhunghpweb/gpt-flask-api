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
    matches = []

    for p in project_list:
        raw_name = p.get("ten_du_an")
        if not raw_name:
            continue

        norm_db_name = normalize_name(raw_name)

        # Nếu tên nhập vào nằm trong tên dự án sau chuẩn hóa
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
    print("🔥 [POST] Nhận yêu cầu thêm sự kiện mới")
    data = request.json
    print("📥 Dữ liệu nhận được:", data)

    short_name = data.get("du_an")
    projects = supabase.table("project").select("id, ten_du_an").execute().data
    matched_project, suggestions = find_best_project(short_name, projects)

    if not matched_project:
        return jsonify({
            "error": "Không tìm thấy dự án phù hợp",
            "suggestions": [p["ten_du_an"] for p in suggestions]
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
            "suggestions": [p["ten_du_an"] for p in suggestions]
        }), 404

    print("✅ Dự án:", matched_project["ten_du_an"])
    events = supabase.table("events").select("*").eq("project_id", matched_project["id"]).execute().data
    print(f"📊 Số sự kiện tìm thấy: {len(events)}")

    return jsonify({
        "project": matched_project["ten_du_an"],
        "so_luong": len(events),
        "events": events
    })

# --- API POST: Thêm dự án ---
@app.route("/project", methods=["POST"])
def add_project():
    try:
        print("🔥 [POST] Nhận yêu cầu thêm dự án mới")
        data = request.json
        print("📥 Dữ liệu nhận:", data)

        ten_du_an = data.get("ten_du_an")
        if not ten_du_an:
            return jsonify({"error": "Thiếu trường 'ten_du_an'"}), 400

        project_data = {
            "ten_du_an": ten_du_an,
            "cong_suat_mva": data.get("cong_suat_mva", None),
            "chieu_dai_km": data.get("chieu_dai_km", None),
            "don_vi_quan_ly": data.get("don_vi_quan_ly", None),
            "so_van_ban_giao_nhiem_vu": data.get("so_van_ban_giao_nhiem_vu", None),
            "ngay_van_ban_giao_nhiem_vu": data.get("ngay_van_ban_giao_nhiem_vu", None),
            "khoi_cong": data.get("khoi_cong", None),
            "hoan_thanh_dong_dien": data.get("hoan_thanh_dong_dien", None)
        }

        supabase.table("project").insert(project_data).execute()
        print("✅ Đã thêm dự án:", ten_du_an)
        return jsonify({"success": True, "ten_du_an": ten_du_an}), 200

    except Exception as e:
        print("❌ Lỗi khi xử lý /project:", str(e))
        return jsonify({"error": "Lỗi máy chủ", "chi_tiet": str(e)}), 500

# --- API GET: Toàn bộ danh sách dự án ---
@app.route("/project-full", methods=["GET"])
def get_all_projects():
    try:
        result = supabase.table("project").select("*").limit(1000).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Chạy local ---
if __name__ == "__main__":
    app.run(debug=True)
