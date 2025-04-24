from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/api/v1/query")
def query():
    query_param = request.args.get("query", "")
    # Return a dummy response that mimics Prometheus
    return jsonify({
        "status": "success",
        "data": {
            "resultType": "vector",
            "result": [
                {
                    "metric": {"__name__": "up", "instance": "localhost:9090"},
                    "value": [1682064000, "1"]
                },
                {
                    "metric": {"__name__": "up", "instance": "localhost:9091"},
                    "value": [1682064001, "0"]
                }
            ]
        }
    })

if __name__ == "__main__":
    app.run(port=9090)
