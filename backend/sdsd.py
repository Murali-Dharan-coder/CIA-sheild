from flask import Flask, request, jsonify
from flask_cors import CORS
import requests, hashlib, time, json
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

# ---------------------- CONFIDENTIALITY CHECK ----------------------
def check_confidentiality(url):
    report, details, score = {}, [], 0
    try:
        response = requests.get(url, timeout=5)
        # HTTPS check
        if url.lower().startswith("https://"):
            score += 50
            details.append("✅ HTTPS detected.")
        else:
            details.append("⚠️ HTTP detected, consider upgrading to HTTPS.")
        # Security header check
        headers = response.headers
        security_headers = [
            "Strict-Transport-Security", "Content-Security-Policy",
            "X-Content-Type-Options", "X-Frame-Options",
            "Referrer-Policy", "Permissions-Policy"
        ]
        found = [h for h in security_headers if h in headers]
        score += 10 * len(found)
        details.append(f"Security headers present: {', '.join(found)}" if found else "No security headers found.")
        report["score"], report["details"] = min(score, 100), details
    except requests.RequestException as e:
        report["error"] = f"Request failed: {e}"
    return report

# ---------------------- INTEGRITY CHECK ----------------------
def check_integrity(url):
    report, details = {}, []
    try:
        response = requests.get(url, timeout=5)
        content = response.content
        content_hash = hashlib.sha256(content).hexdigest()
        details.append(f"SHA256 hash: {content_hash}")
        score = 80 if len(content) > 0 else 40
        details.append("Content integrity looks good." if score == 80 else "Potential integrity issue.")
        report["score"], report["details"] = score, details
    except requests.RequestException as e:
        report["error"] = f"Request failed: {e}"
    return report

# ---------------------- AVAILABILITY CHECK ----------------------
def check_availability(url):
    report, details, score = {}, [], 0
    try:
        start = time.time()
        response = requests.get(url, timeout=5)
        elapsed = time.time() - start
        if response.status_code == 200:
            score += 50
            details.append("✅ HTTP 200 OK.")
        else:
            details.append(f"⚠️ HTTP status: {response.status_code}")
        # Response time
        if elapsed < 0.5:
            score += 50
            details.append(f"Fast ({elapsed:.2f}s).")
        elif elapsed < 1.5:
            score += 30
            details.append(f"Moderate ({elapsed:.2f}s).")
        else:
            details.append(f"Slow ({elapsed:.2f}s).")
        report["score"], report["details"] = min(score, 100), details
    except requests.RequestException as e:
        report["error"] = f"Request failed: {e}"
    return report

# ---------------------- MAIN ANALYSIS ROUTE ----------------------
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    url, test_type = data.get("url"), data.get("test_type")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    parsed = urlparse(url)
    domain = parsed.netloc or "unknown"

    def format_result(report, name):
        if "error" in report:
            return report
        score, details = report["score"], " ".join(report["details"])
        return {
            "score": score,
            "one_line": f"{name} score: {score}/100 for {domain}.",
            "explanation": f"{name} check for {url}: {details}",
            "suggestion": f"Improve {name.lower()} by applying best security practices."
        }

    if test_type == "confidentiality":
        result = format_result(check_confidentiality(url), "Confidentiality")
    elif test_type == "integrity":
        result = format_result(check_integrity(url), "Integrity")
    elif test_type == "availability":
        result = format_result(check_availability(url), "Availability")
    elif test_type == "cia":
        conf = format_result(check_confidentiality(url), "Confidentiality")
        integ = format_result(check_integrity(url), "Integrity")
        avail = format_result(check_availability(url), "Availability")
        if all("score" in r for r in [conf, integ, avail]):
            overall = (conf["score"] + integ["score"] + avail["score"]) // 3
        else:
            overall = None
        result = {
            "score": overall,
            "one_line": f"Full CIA check for {domain}: {overall}/100." if overall else "Error calculating overall score.",
            "details": {"confidentiality": conf, "integrity": integ, "availability": avail}
        }
    else:
        result = {"error": "Unknown test type"}

    return jsonify(result)

# ---------------------- RUN APP ----------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
