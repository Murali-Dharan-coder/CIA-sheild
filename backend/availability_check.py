import requests
import time
import json

def check_availability(url):
    """
    Check availability aspects of the website.
    For example, measure response time and HTTP status.
    Returns a report dict with score and details, and prints the report.
    """
    report = {}
    score = 0
    details = []

    try:
        start = time.time()
        response = requests.get(url, timeout=5)
        elapsed = time.time() - start

        # Check HTTP status code
        if response.status_code == 200:
            score += 50
            details.append("HTTP 200 OK received.")
        else:
            details.append(f"HTTP status code: {response.status_code}")

        # Score based on response time (lower is better)
        if elapsed < 0.5:
            score += 50
            details.append(f"Fast response time: {elapsed:.2f} seconds.")
        elif elapsed < 1.5:
            score += 30
            details.append(f"Moderate response time: {elapsed:.2f} seconds.")
        else:
            details.append(f"Slow response time: {elapsed:.2f} seconds.")

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
