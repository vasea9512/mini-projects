# server.py
from flask import Flask, request, jsonify

app = Flask(__name__)

rankings = []

@app.route("/add", methods=["POST"])
def add_score():
    data = request.get_json()
    name = data.get("name")
    score = data.get("score", 0)
    rankings.append({"name": name, "score": score})
    rankings.sort(key=lambda x: x["score"], reverse=True)
    return jsonify({"status": "ok"})

@app.route("/top", methods=["GET"])
def top_scores():
    return jsonify(rankings[:10])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)