// This file runs in the browser.
// It calls your backend API endpoints and updates the page.
function $(id) {
 return document.getElementById(id);
}
function show(el) {
 el.classList.remove("d-none");
}
function hide(el) {
 el.classList.add("d-none");
}
function setAlertStyleBySeverity(alertEl, severity) {
 // TfL severity scale varies, but lower is usually better.
 // Keep the mapping simple and explainable.
 alertEl.classList.remove("alert-success", "alert-warning", "alert-danger", "alert-info");
 if (severity <= 5) alertEl.classList.add("alert-success");
 else if (severity <= 9) alertEl.classList.add("alert-warning");
 else alertEl.classList.add("alert-danger");
}
async function fetchJson(url) {
 const res = await fetch(url);
 const body = await res.json().catch(() => ({}));
 return { res, body };
}
async function checkStatus() {
 hide($("errorPanel"));
 hide($("statusPanel"));
 const lineId = $("lineSelect").value;
 const { res, body } = await fetchJson(`/line-status?line_id=${encodeURIComponent(lineId)}`);
 if (!res.ok) {
   $("errorText").textContent = body.detail || `Request failed with HTTP ${res.status}`;
   show($("errorPanel"));
   return;
 }
 $("statusLine").textContent = body.line_id;
 $("statusText").textContent = body.status;
 $("statusSeverity").textContent = body.severity;
 $("statusTime").textContent = body.requested_at;
 const reason = body.reason;
 if (reason) {
   $("statusReason").textContent = reason;
   show($("statusReasonWrap"));
 } else {
   hide($("statusReasonWrap"));
 }
 setAlertStyleBySeverity($("statusAlert"), body.severity);
 show($("statusPanel"));
 // Update history after a successful status check.
 await loadHistory();
}
async function loadHistory() {
 const { res, body } = await fetchJson(`/history?limit=20`);
 const tbody = $("historyBody");
 tbody.innerHTML = "";
 if (!res.ok) {
   tbody.innerHTML = `<tr><td colspan="4" class="text-danger">Could not load history (HTTP ${res.status}).</td></tr>`;
   return;
 }
 if (!Array.isArray(body) || body.length === 0) {
   tbody.innerHTML = `<tr><td colspan="4" class="text-muted">No data yet.</td></tr>`;
   $("historyMeta").textContent = "";
   return;
 }
 for (const row of body) {
   const tr = document.createElement("tr");
   tr.innerHTML = `
<td class="text-muted small">${row.requested_at}</td>
<td>${row.line_id}</td>
<td>${row.status}</td>
<td>${row.severity}</td>
   `;
   tbody.appendChild(tr);
 }
 $("historyMeta").textContent = `showing ${body.length} records`;
}
document.addEventListener("DOMContentLoaded", () => {
 $("checkBtn").addEventListener("click", checkStatus);
 $("refreshHistoryBtn").addEventListener("click", loadHistory);
 // Load history on page load (useful visual proof).
 loadHistory();
});