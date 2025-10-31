import requests
import hashlib
import json

def check_integrity(url):
    """
    Check integrity aspects of the website.
    For example, fetch the homepage content and compute a hash.
    Returns a report dict with score and details, and prints the report.
    """
    report = {}
    score = 0
    details = []

    try:
        response = requests.get(url, timeout=5)
        content = response.content
        # Compute SHA256 hash of content
        content_hash = hashlib.sha256(content).hexdigest()
        details.append(f"SHA256 hash of content: {content_hash}")

        # For demo, assume if content length > 0, integrity is good
        if len(content) > 0:
            score = 80
            details.append("Content fetched successfully, integrity likely good.")
        else:
            score = 40
            details.append("Empty content, potential integrity issue.")

    except requests.RequestException as e:
        report["error"] = f"Request failed: {str(e)}"
        print(json.dumps(report, indent=2))
        return report

    report["score"] = score
    report["details"] = details
    print(json.dumps(report, indent=2))
    return report
