from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import hashlib
from confidentiality_check import check_confidentiality
from integrity_check import check_integrity
from availability_check import check_availability

app = Flask(__name__)
CORS(app)  # allow frontend to connect

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    url = data.get("url")
    test_type = data.get("test_type")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Parse URL for more details
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path
        scheme = parsed.scheme
    except:
        domain = "unknown"
        path = ""
        scheme = "http"

    if test_type == "confidentiality":
        report = check_confidentiality(url)
        if "error" in report:
            result = report
        else:
            score = report["score"]
            details = " ".join(report["details"])
            result = {
                "score": score,
                "one_line": f"Confidentiality score: {score}/100 for {domain}.",
                "explanation": f"Analysis of {url}: {details}",
                "suggestion": f"For {domain}, {'maintain current practices' if score > 70 else 'implement HTTPS and add security headers'}."
            }
    elif test_type == "integrity":
        report = check_integrity(url)
        if "error" in report:
            result = report
        else:
            score = report["score"]
            details = " ".join(report["details"])
            result = {
                "score": score,
                "one_line": f"Integrity score: {score}/100 for {domain}.",
                "explanation": f"Integrity check for {url}: {details}",
                "suggestion": f"Enhance integrity for {domain} by {'using strong hashing' if score <= 75 else 'continuing with current measures'}."
            }
    elif test_type == "availability":
        report = check_availability(url)
        if "error" in report:
            result = report
        else:
            score = report["score"]
            details = " ".join(report["details"])
            result = {
                "score": score,
                "one_line": f"Availability score: {score}/100 for {domain}.",
                "explanation": f"Availability assessment for {url}: {details}",
                "suggestion": f"Improve availability for {domain} by {'adding caching and optimization' if score <= 80 else 'maintaining uptime'}."
            }
    elif test_type == "cia":
        conf_report = check_confidentiality(url)
        int_report = check_integrity(url)
        avail_report = check_availability(url)

        def format_result(report, name, domain, url):
            if "error" in report:
                return report
            score = report["score"]
            details = " ".join(report["details"])
            return {
                "score": score,
                "one_line": f"{name} score: {score}/100 for {domain}.",
                "explanation": f"{name} check for {url}: {details}",
                "suggestion": f"Improve {name.lower()} for {domain}."
            }

        conf_result = format_result(conf_report, "Confidentiality", domain, url)
        int_result = format_result(int_report, "Integrity", domain, url)
        avail_result = format_result(avail_report, "Availability", domain, url)

        if "score" in conf_result and "score" in int_result and "score" in avail_result:
            overall_score = (conf_result["score"] + int_result["score"] + avail_result["score"]) // 3
        else:
            overall_score = None

        result = {
            "score": overall_score,
            "one_line": f"Full CIA check for {domain}: Overall {overall_score}/100." if overall_score is not None else "Error calculating overall score.",
            "details": {
                "confidentiality": conf_result,
                "integrity": int_result,
                "availability": avail_result
            }
        }
    else:
        result = {"error": "Unknown test type"}

    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
