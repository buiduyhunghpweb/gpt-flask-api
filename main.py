@app.route("/api", methods=["POST"])
def handle_request():
    try:
        data = request.get_json(force=True)
        print("✅ Nhận dữ liệu từ GPT:")
        print(data)

        # Trích xuất các trường cụ thể
        project = data.get("project", {})
        print("==> Thông tin dự án:")
        print(f"- Tên: {project.get('ten')}")
        print(f"- Quy mô: {project.get('quy_mo')}")
        print(f"- Tiến độ: {project.get('tien_do')}")

        return jsonify({
            "status": "ok",
            "message": "GPT gửi dữ liệu thành công!",
            "received": data
        }), 200

    except Exception as e:
        print("❌ Lỗi khi xử lý request:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500
