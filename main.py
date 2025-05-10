from flask import Flask, request, jsonify

app = Flask(__name__)

# Giả sử lưu các dự án ở đây (bộ nhớ tạm)
projects = []

@app.route("/api", methods=["POST"])
def handle_request():
    data = request.get_json()
    print("==> Dữ liệu GPT gửi:", data)

    command = data.get("command", "")
    
    if command == "thêm dự án":
        project = data.get("project", {})
        projects.append(project)
        return jsonify({
            "status": "ok",
            "message": "Đã thêm dự án mới!",
            "received": project
        }), 200

    elif command == "truy vấn tất cả dự án":
        return jsonify({
            "status": "ok",
            "projects": projects
        }), 200

    else:
        return jsonify({
            "status": "error",
            "message": f"Command không hợp lệ: {command}"
        }), 400

if __name__ == "__main__":
    app.run()
