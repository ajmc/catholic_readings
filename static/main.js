// Format date to friendly "Month Day, Year"
function formatDate(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric"
  });
}

// Convert underscores to capitalized words
function humanize(str) {
  return str
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

// Formats cycle values to be more human-readable
function formatCycleValue(value) {
  if (!value) return "";
  return value
    .replace(/_/g, " ")
    .replace(/\bYEAR ([A-Z])\b/, "Year $1")
    .replace(/\bYEAR (\d)\b/, "Year $1")
    .replace(/\bWEEK (\d)\b/, (_, num) => {
      const roman = ["I","II","III","IV"][parseInt(num,10)-1] || num;
      return `Week ${roman}`;
    });
}

// Map liturgical color text → hex code
const colorMap = {
  WHITE: "#ffffff",
  GREEN: "#2ecc71",
  RED: "#e74c3c",
  PURPLE: "#8e44ad",
  PINK: "#ff69b4",
  BLACK: "#000000",
  GOLD: "#ffd700"
};

// Create swatch for colors
function renderColors(colors) {
  return `
    <div class="color-list">
      ${colors
        .map(
          (c) => `
        <div class="swatch" style="background-color: ${colorMap[c] || "#ccc"}"></div>
        <span class="swatch-label">${humanize(c)}</span>
      `
        )
        .join("")}
    </div>
  `;
}

// Render cycles as key-value pairs
function renderCycles(cycles) {
  return `
    <div class="cycles">
      <p><strong>Cycles</strong></p>
      ${Object.entries(cycles)
        .map(([k, v]) => `<p>${humanize(k)}: ${humanize(v)}</p>`)
        .join("")}
    </div>
  `;
}

// Fetch today's Ordo
async function fetchOrdoToday() {
  const container = document.getElementById("ordoContainer");

  try {
    const response = await fetch("/ordo/today");
    const data = await response.json();

    if (data.length === 0) {
      container.innerHTML = "<p>No entries for today.</p>";
      return;
    }

    container.innerHTML = "";
    data.forEach((entry) => {
      const div = document.createElement("div");
      div.className = "ordo-entry";

  const cycles = entry.cycles || {};
        const cyclesHtml = `
          <h3>Liturgical Cycles</h3>
          <ul>
            <li><strong>Proper Cycle:</strong> ${formatCycleValue(cycles.properCycle)}</li>
            <li><strong>Sunday Cycle:</strong> ${formatCycleValue(cycles.sundayCycle)}</li>
            <li><strong>Weekday Cycle:</strong> ${formatCycleValue(cycles.weekdayCycle)}</li>
            <li><strong>Psalter Week:</strong> ${formatCycleValue(cycles.psalterWeek)}</li>
          </ul>
        `;
	    

      div.innerHTML += `
        <div class="entry-row">
          <div class="title-and-meta">
            <h2 class="entry-title">${humanize(entry.id)}</h2>
            <p class="meta">${formatDate(entry.date)}</p>
            <p><strong>Rank:</strong> ${humanize(entry.rank)}</p>
            <p><strong>Season:</strong> ${entry.seasons.map(humanize).join(", ")}</p>
            ${renderColors(entry.colors)}
          </div>
          ${renderCycles(entry.cycles)}
        </div>
      `;

      container.appendChild(div);
    });
  } catch (err) {
    console.error("Error fetching ordo:", err);
    container.innerHTML = "<p>Error loading entries.</p>";
  }
}

// Dark mode toggle
document.addEventListener("DOMContentLoaded", () => {
  const toggleBtn = document.getElementById("toggleTheme");

  toggleBtn.addEventListener("click", () => {
    if (document.documentElement.getAttribute("data-theme") === "dark") {
      document.documentElement.removeAttribute("data-theme");
    } else {
      document.documentElement.setAttribute("data-theme", "dark");
    }
  });

  fetchOrdoToday();
});

