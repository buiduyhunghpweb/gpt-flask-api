from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api", methods=["POST"])
def handle_request():
    data = request.get_json()
    print("==> Dữ liệu GPT gửi:", data)

    if data.get("command") == "thêm dự án":
        return jsonify({
            "status": "đã là bản mới nhất rồi",
            "message": "Dự án đã được thêm thành công.",
            "received": data
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Lệnh không hợp lệ.",
            "received": data
        }), 400

if __name__ == "__main__":
    app.run()
