from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api", methods=["POST"])
def handle_request():
    data = request.get_json()
    print("==> Dữ liệu GPT gửi:", data)

    return jsonify({
        "status": "ok",
        "message": "GPT gửi dữ liệu thành công!",
        "received": data
    }), 200

if __name__ == "__main__":
    app.run()
