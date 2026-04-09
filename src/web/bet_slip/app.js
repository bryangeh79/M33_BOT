function getQueryParam(name) {
  const params = new URLSearchParams(window.location.search);
  return params.get(name);
}

function safeJsonParse(value, fallback = null) {
  try {
    return JSON.parse(value);
  } catch (error) {
    return fallback;
  }
}

function getBetSlipData() {
  const queryData = getQueryParam("data");
  if (queryData) {
    const decoded = decodeURIComponent(queryData);
    const parsed = safeJsonParse(decoded, null);
    if (parsed) {
      return parsed;
    }
  }

  if (window.__BET_SLIP_DATA__) {
    return window.__BET_SLIP_DATA__;
  }

  // fallback demo
  return {
    region: "MN",
    ticket: "N6",
    target_date: null,
    rows: [
      { mode: "DN", numbers: "11 22", type: "LO", bet: "10N", amount: "180" },
      { mode: "DN", numbers: "11 23 22", type: "LO", bet: "10N", amount: "270" }
    ],
    total: "450"
  };
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function buildSlipText(data) {
  const lines = [];
  lines.push("✅ Bet Accepted");
  lines.push(`${data.region} · ${data.ticket}`);

  if (data.target_date) {
    lines.push(`Date: ${data.target_date}`);
  }

  lines.push("");

  for (const row of data.rows || []) {
    lines.push(
      `${row.mode} · ${row.numbers} · ${row.type} · ${row.bet} · ${row.amount}`
    );
  }

  lines.push("");
  lines.push(`Total: ${data.total}`);

  return lines.join("\n");
}

function renderTableRows(data) {
  const tbody = document.getElementById("tableBody");

  if (!data.rows || data.rows.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5">
          <div class="empty-state">No bet rows found.</div>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = data.rows
    .map(
      (row) => `
        <tr>
          <td>${escapeHtml(row.mode)}</td>
          <td>${escapeHtml(row.numbers)}</td>
          <td>${escapeHtml(row.type)}</td>
          <td>${escapeHtml(row.bet)}</td>
          <td class="amount">${escapeHtml(row.amount)}</td>
        </tr>
      `
    )
    .join("");
}

function renderPage(data) {
  const subtitle = document.getElementById("subTitle");
  const dateLine = document.getElementById("dateLine");
  const totalAmount = document.getElementById("totalAmount");

  subtitle.textContent = `${data.region || "--"} · ${data.ticket || "--"}`;

  if (data.target_date) {
    dateLine.textContent = `Date: ${data.target_date}`;
    dateLine.classList.remove("hidden");
  } else {
    dateLine.classList.add("hidden");
  }

  totalAmount.textContent = data.total || "0";
  renderTableRows(data);
}

async function copySlip(data) {
  const copyBtn = document.getElementById("copyBtn");
  const text = buildSlipText(data);

  try {
    await navigator.clipboard.writeText(text);
    const oldText = copyBtn.textContent;
    copyBtn.textContent = "Copied";
    copyBtn.classList.add("success");

    setTimeout(() => {
      copyBtn.textContent = oldText;
      copyBtn.classList.remove("success");
    }, 1400);
  } catch (error) {
    alert("Copy failed.");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const data = getBetSlipData();
  renderPage(data);

  const copyBtn = document.getElementById("copyBtn");
  copyBtn.addEventListener("click", () => copySlip(data));
});