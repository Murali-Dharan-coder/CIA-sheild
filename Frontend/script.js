function runAnalysis(type) {
  const resultsBox = document.getElementById("results");
  resultsBox.style.display = "block";

  const urlInput = document.getElementById("urlInput").value.trim();

  if (!urlInput) {
    resultsBox.innerHTML = '<p class="error-message">Please enter the URL.</p>';
    return;
  }

  // Simple URL validation
  try {
    new URL(urlInput);
  } catch (e) {
    resultsBox.innerHTML = '<p class="error-message">Please enter a valid URL.</p>';
    return;
  }

  const testType = type === "all" ? "cia" : type;

  fetch('http://localhost:5000/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ url: urlInput, test_type: testType })
  })
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      resultsBox.innerHTML = `<p class="error-message">${data.error}</p>`;
      return;
    }

    let output = "";

    if (data.details) {
      // For CIA full check
      const sections = [
        { key: 'confidentiality', icon: '🔒', title: 'Confidentiality' },
        { key: 'integrity', icon: '🛡', title: 'Integrity' },
        { key: 'availability', icon: '⚡', title: 'Availability' }
      ];
      sections.forEach(section => {
        const score = data.details[section.key];
        output += `
          <div class="cia-section">
            <h4>${section.icon} ${section.title}</h4>
            <div class="score">${score.score} / 100</div>
            <div class="progress-bar"><div class="progress-bar-inner" style="width:${score.score}%;"></div></div>
            <p><strong>One-line:</strong> ${score.one_line}</p>
            <p><strong>Explanation:</strong> ${score.explanation}</p>
            <p><strong>Suggestion:</strong> ${score.suggestion}</p>
          </div>`;
      });
    } else {
      // For individual checks
      const icons = {
        confidentiality: '🔒',
        integrity: '🛡',
        availability: '⚡'
      };
      const titles = {
        confidentiality: 'Confidentiality',
        integrity: 'Integrity',
        availability: 'Availability'
      };
      output += `
        <div class="cia-section">
          <h4>${icons[type]} ${titles[type]}</h4>
          <div class="score">${data.score} / 100</div>
          <div class="progress-bar"><div class="progress-bar-inner" style="width:${data.score}%;"></div></div>
          <p><strong>One-line:</strong> ${data.one_line}</p>
          <p><strong>Explanation:</strong> ${data.explanation}</p>
          <p><strong>Suggestion:</strong> ${data.suggestion}</p>
        </div>`;
    }

    resultsBox.innerHTML = output;
  })
  .catch(error => {
    resultsBox.innerHTML = '<p class="error-message">Error connecting to server. Please try again.</p>';
    console.error('Error:', error);
  });
}
