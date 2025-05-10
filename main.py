from flask import Flask, request, jsonify
from supabase import create_client, Client
from rapidfuzz import process

# --- Cấu hình Supabase ---
SUPABASE_URL = "https://skrmxsdfimvelnkrnhif.supabase.co"  # Thay bằng URL thật của bạn
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."    # Thay bằng key thật

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app = Flask(__name__)

# --- Hàm chuẩn hóa tên ---
def normalize_name(name: str) -> str:
    name = name.lower()
    name = name.replace("trạm biến áp", "tba")
    name = name.replace("trạm", "tba")
    name = name.replace("đường dây đấu nối", "")
    name = name.replace("đường dây", "")
    name = name.replace("giai đoạn", "")
    name = name.replace("và", "")
    name = name.replace("-", "")
    name = name.replace("500 kv", "500kv")
    name = name.replace("220 kv", "220kv")
    name = name.replace(" ", "")
    return name

# --- Tìm dự án phù hợp ---
def find_best_project(input_text: str, project_list: list):
    norm_input = normalize_name(input_text)
    print(f"🔍 Tìm dự án cho: '{input_text}' → '{norm_input}'")

    normalized_projects = [
        {
            "project": p,
            "normalized_name": normalize_name(p["ten_du_an"])
        } for p in project_list
    ]
    norm_names = [p["normalized_name"] for p in normalized_projects]
    result = process.extractOne(norm_input, norm_names)

    if result:
        score = result[1]
        index = norm_names.index(result[0])
        matched_project = normalized_projects[index]["project"]
        print(f"✅ Gần đúng nhất: {matched_project['ten_du_an']} (score = {score})")
        if score > 70:
            return matched_project

    print("❌ Không tìm thấy dự án phù hợp.")
    return None

# --- API: Thêm event ---
@app.route("/event", methods=["POST"])
def add_event():
    print("🔥 [POST] Nhận yêu cầu thêm sự kiện mới")
    data = request.json
    print("📥 Dữ liệu nhận được:", data)

    short_name = data.get("du_an")
    projects = supabase.table("projects").select("*").execute().data
    matched_project = find_best_project(short_name, projects)

    if not matched_project:
        return jsonify({"error": "Không tìm thấy dự án phù hợp"}), 404

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

# --- API: Lấy danh sách event ---
@app.route("/event", methods=["GET"])
def list_events():
    print("🔍 [GET] Nhận yêu cầu lấy danh sách sự kiện")
    short_name = request.args.get("du_an")
    print("📥 Tham số dự án:", short_name)

    projects = supabase.table("projects").select("*").execute().data
    matched_project = find_best_project(short_name, projects)

    if not matched_project:
        return jsonify({"error": "Không tìm thấy dự án phù hợp"}), 404

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
