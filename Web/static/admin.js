let pieChart = null;
let lineChart = null;

function loadAdminHistory() {
  const from = document.getElementById("dateFrom").value;
  const to = document.getElementById("dateTo").value;
  const sentiment = document.getElementById("filterSentiment").value;
  const topic = document.getElementById("filterTopic").value;
  let url = "/admin/api/history?limit=200";
  if (from) url += "&date_from=" + from;
  if (to) url += "&date_to=" + to;
  if (sentiment) url += "&sentiment=" + sentiment;
  if (topic) url += "&topic=" + topic;

  fetch(url).then(r=>r.json()).then(data=>{
    const tbody = document.getElementById("adminTable");
    tbody.innerHTML = "";
    data.forEach(it=>{
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${it.id}</td>
                      <td>${it.sentiment}</td>
                      <td>${it.topic}</td>
                      <td>${it.created_at}</td>
                      <td>${it.ip_address}</td>
                      <td><button class="btn btn-sm btn-info" onclick="showFullText('${it.text.replace(/'/g, "\\'")}')">Xem</button></td>
                      <td><button class="btn btn-sm btn-danger" onclick="deleteRow(${it.id})">Xóa</button></td>`;
      tbody.appendChild(tr);
    });
  }).catch(e=>console.error(e));
}

function showFullText(text) {
  alert(text);
}

function deleteRow(id) {
  if (!confirm("Bạn có chắc muốn xóa bản ghi này?")) return;
  fetch("/admin/api/delete", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({id: id})
  }).then(r=>r.json()).then(res=>{
    if (res.ok) {
      loadAdminHistory();
      loadStats();
    } else {
      alert("Lỗi xóa: " + (res.error || JSON.stringify(res)));
    }
  });
}

function loadStats() {
  fetch("/admin/api/stats").then(r=>r.json()).then(data=>{
    const sent = data.sentiment_counts || {};
    const labels = Object.keys(sent);
    const values = labels.map(l => sent[l]);

    // Pie chart
    const ctx = document.getElementById("pieChart").getContext("2d");
    if (pieChart) pieChart.destroy();
    pieChart = new Chart(ctx, {
      type: 'pie',
      data: { labels: labels, datasets: [{ data: values, backgroundColor: ['#dc3545', '#ffc107', '#198754'] }] },
      options: { responsive: true, plugins: { legend: { position: 'top' } } }
    });

    // Trend
    fetch("/admin/api/trend?days=30").then(r=>r.json()).then(tr=>{
      if (tr.error) return;
      const dates = tr.dates;
      const datasetsObj = tr.datasets;
      const keys = Object.keys(datasetsObj);
      const ds = keys.map((k, idx) => ({
        label: k,
        data: datasetsObj[k],
        fill: false,
        tension: 0.2,
        borderColor: ['#dc3545', '#ffc107', '#198754'][idx],
        backgroundColor: ['#dc3545', '#ffc107', '#198754'][idx]
      }));
      const ctx2 = document.getElementById("lineChart").getContext("2d");
      if (lineChart) lineChart.destroy();
      lineChart = new Chart(ctx2, {
        type: 'line',
        data: { labels: dates, datasets: ds },
        options: { responsive: true, scales: { x: { display: true } } }
      });
    });
  });
}

// init
window.onload = function(){
  loadAdminHistory();
  loadStats();
}