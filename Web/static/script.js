// Load history
function loadHistory() {
  fetch("/history?limit=50")
    .then(r => r.json())
    .then(data => {
      const ul = document.getElementById("historyList");
      ul.innerHTML = "";
      data.forEach(it => {
        const li = document.createElement("li");
        li.className = "list-group-item";
        li.innerHTML = `<div><strong>${it.sentiment}</strong> — <small>${it.topic}</small></div>
                        <div>${it.text}</div>
                        <div class="text-muted small">${it.created_at}</div>`;
        ul.appendChild(li);
      });
    })
    .catch(err => console.error("Lỗi load lịch sử:", err));
}

function analyzeFeedback() {
  const text = document.getElementById("feedback").value.trim();
  if (!text) { alert("Vui lòng nhập góp ý"); return; }

  // Hiển thị loading spinner và ẩn nút
  document.getElementById("analyzeBtn").classList.add("d-none");
  document.getElementById("loadingSpinner").classList.remove("d-none");
  document.getElementById("result").classList.add("d-none");

  fetch("/predict", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({text: text})
  })
  .then(r => r.json())
  .then(data => {
    // Ẩn loading spinner và hiển thị lại nút
    document.getElementById("analyzeBtn").classList.remove("d-none");
    document.getElementById("loadingSpinner").classList.add("d-none");
    
    if (data.error) { alert("Lỗi: " + data.error); return; }
    document.getElementById("result").classList.remove("d-none");
    document.getElementById("sentiment").innerText = data.sentiment;
    document.getElementById("topic").innerText = data.topic;
    document.getElementById("feedback").value = "";
    loadHistory();
  })
  .catch(err => {
    // Ẩn loading spinner và hiển thị lại nút ngay cả khi có lỗi
    document.getElementById("analyzeBtn").classList.remove("d-none");
    document.getElementById("loadingSpinner").classList.add("d-none");
    alert("Lỗi: " + err);
  });
}

window.onload = loadHistory;