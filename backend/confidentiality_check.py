import requests
import json

def check_confidentiality(url):
    """
    Check confidentiality aspects of the website.
    For example, check if HTTPS is used and if security headers are present.
    Returns a report dict with score and details, and prints the report.
    """
    report = {}
    score = 0
    details = []

    try:
        response = requests.get(url, timeout=5)
        # Check if HTTPS
        if url.lower().startswith("https://"):
            score += 50
            details.append("HTTPS detected, improving confidentiality.")
        else:
            details.append("HTTP detected, consider upgrading to HTTPS.")

        # Check security headers
        security_headers = [
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "X-Content-Type-Options",
            "X-Frame-Options",
            "Referrer-Policy",
            "Permissions-Policy"
        ]
        headers = response.headers
        present_headers = [h for h in security_headers if h in headers]
        score += 10 * len(present_headers)
        if present_headers:
            details.append(f"Security headers present: {', '.join(present_headers)}.")
        else:
            details.append("No important security headers detected.")

        # Cap score at 100
        if score > 100:
            score = 100

    except requests.RequestException as e:
        report["error"] = f"Request failed: {str(e)}"
        print(json.dumps(report, indent=2))
        return report

    report["score"] = score
    report["details"] = details
    print(json.dumps(report, indent=2))
    return report
