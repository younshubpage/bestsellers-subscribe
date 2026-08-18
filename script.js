/* ==========================================================
   ⚠️ 실제 서비스로 바꾸는 방법
   지금은 SAMPLE_DATA 안에 가짜 순위가 날짜별로 들어있습니다.
   나중에 각 서점에서 실제 데이터를 수집하게 되면(크레마클럽/
   밀리의서재/sam 프리미엄/sam 무제한), 아래 SAMPLE_DATA 객체를
   같은 구조({"YYYY-MM-DD": {소스명: [ {rank, title, author}, ... ]}})의
   진짜 JSON으로 통째로 교체하면 됩니다. 이 아래의 렌더링 코드는
   전혀 손댈 필요가 없습니다.
   ========================================================== */

const SOURCES = ["크레마클럽", "밀리의서재", "sam 프리미엄", "sam 무제한"];

const SAMPLE_DATA = {
  "2026-08-18": {
    "크레마클럽": [
      { rank: 1, title: "여름의 이름들", author: "김소림" },
      { rank: 2, title: "우주정거장의 저녁 식사", author: "박도윤" },
      { rank: 3, title: "고요한 오후 세 시", author: "이하린" },
      { rank: 4, title: "작은 집, 큰 마음", author: "정우재" },
      { rank: 5, title: "밤의 지도", author: "한서연" },
    ],
    "밀리의서재": [
      { rank: 1, title: "우주정거장의 저녁 식사", author: "박도윤" },
      { rank: 2, title: "여름의 이름들", author: "김소림" },
      { rank: 3, title: "두 번째 서랍", author: "최윤아" },
      { rank: 4, title: "고요한 오후 세 시", author: "이하린" },
      { rank: 5, title: "그 여름, 두 사람", author: "오지훈" },
    ],
    "sam 프리미엄": [
      { rank: 1, title: "여름의 이름들", author: "김소림" },
      { rank: 2, title: "작은 집, 큰 마음", author: "정우재" },
      { rank: 3, title: "밤의 지도", author: "한서연" },
      { rank: 4, title: "우주정거장의 저녁 식사", author: "박도윤" },
      { rank: 5, title: "회계사의 은퇴 노트", author: "강민석" },
    ],
    "sam 무제한": [
      { rank: 1, title: "두 번째 서랍", author: "최윤아" },
      { rank: 2, title: "여름의 이름들", author: "김소림" },
      { rank: 3, title: "그 여름, 두 사람", author: "오지훈" },
      { rank: 4, title: "고요한 오후 세 시", author: "이하린" },
      { rank: 5, title: "밤의 지도", author: "한서연" },
    ],
  },
  "2026-08-17": {
    "크레마클럽": [
      { rank: 1, title: "우주정거장의 저녁 식사", author: "박도윤" },
      { rank: 2, title: "여름의 이름들", author: "김소림" },
      { rank: 3, title: "밤의 지도", author: "한서연" },
      { rank: 4, title: "고요한 오후 세 시", author: "이하린" },
      { rank: 5, title: "작은 집, 큰 마음", author: "정우재" },
    ],
    "밀리의서재": [
      { rank: 1, title: "여름의 이름들", author: "김소림" },
      { rank: 2, title: "우주정거장의 저녁 식사", author: "박도윤" },
      { rank: 3, title: "고요한 오후 세 시", author: "이하린" },
      { rank: 4, title: "두 번째 서랍", author: "최윤아" },
      { rank: 5, title: "밤의 지도", author: "한서연" },
    ],
    "sam 프리미엄": [
      { rank: 1, title: "밤의 지도", author: "한서연" },
      { rank: 2, title: "여름의 이름들", author: "김소림" },
      { rank: 3, title: "작은 집, 큰 마음", author: "정우재" },
      { rank: 4, title: "고요한 오후 세 시", author: "이하린" },
      { rank: 5, title: "우주정거장의 저녁 식사", author: "박도윤" },
    ],
    "sam 무제한": [
      { rank: 1, title: "그 여름, 두 사람", author: "오지훈" },
      { rank: 2, title: "두 번째 서랍", author: "최윤아" },
      { rank: 3, title: "여름의 이름들", author: "김소림" },
      { rank: 4, title: "밤의 지도", author: "한서연" },
      { rank: 5, title: "고요한 오후 세 시", author: "이하린" },
    ],
  },
};

const AVAILABLE_DATES = Object.keys(SAMPLE_DATA).sort().reverse(); // 최신 날짜가 0번
let dateIndex = 0;

const dateLabel = document.getElementById("currentDate");
const prevBtn = document.getElementById("prevDate");
const nextBtn = document.getElementById("nextDate");
const tbody = document.getElementById("ledgerBody");

function formatDate(isoDate) {
  const [y, m, d] = isoDate.split("-");
  return `${y}.${m}.${d}`;
}

/** 어제 순위와 비교해 변동 스탬프 정보를 계산 */
function getDelta(source, book, todayISO, yesterdayISO) {
  const yesterdayList = SAMPLE_DATA[yesterdayISO]?.[source];
  if (!yesterdayList) return null;
  const prev = yesterdayList.find((b) => b.title === book.title);
  if (!prev) return { type: "new" };
  const diff = prev.rank - book.rank; // 양수면 상승
  if (diff === 0) return { type: "same" };
  return { type: diff > 0 ? "up" : "down", amount: Math.abs(diff) };
}

function stampHTML(delta) {
  if (!delta) return "";
  if (delta.type === "new") return `<span class="stamp stamp-new">NEW</span>`;
  if (delta.type === "same") return `<span class="stamp stamp-same">–</span>`;
  if (delta.type === "up") return `<span class="stamp stamp-up">▲${delta.amount}</span>`;
  return `<span class="stamp stamp-down">▼${delta.amount}</span>`;
}

function render() {
  const todayISO = AVAILABLE_DATES[dateIndex];
  const yesterdayISO = AVAILABLE_DATES[dateIndex + 1];
  dateLabel.textContent = formatDate(todayISO);

  prevBtn.disabled = dateIndex >= AVAILABLE_DATES.length - 1;
  nextBtn.disabled = dateIndex <= 0;
  prevBtn.style.opacity = prevBtn.disabled ? 0.35 : 1;
  nextBtn.style.opacity = nextBtn.disabled ? 0.35 : 1;

  const dayData = SAMPLE_DATA[todayISO];
  const maxRank = Math.max(...SOURCES.map((s) => dayData[s]?.length || 0));

  let rows = "";
  for (let rank = 1; rank <= maxRank; rank++) {
    rows += `<tr><td class="col-rank">${rank}</td>`;
    SOURCES.forEach((source) => {
      const book = dayData[source]?.find((b) => b.rank === rank);
      if (!book) {
        rows += `<td class="cell-empty">—</td>`;
        return;
      }
      const delta = getDelta(source, book, todayISO, yesterdayISO);
      rows += `
        <td>
          <div class="cell-with-stamp">
            ${stampHTML(delta)}
            <div class="cell-book">
              <span class="book-title">${book.title}</span>
              <span class="book-author">${book.author}</span>
            </div>
          </div>
        </td>`;
    });
    rows += `</tr>`;
  }
  tbody.innerHTML = rows;
}

function downloadCSV() {
  const todayISO = AVAILABLE_DATES[dateIndex];
  const rows = [["순위", ...SOURCES]];
  const dayData = SAMPLE_DATA[todayISO];
  const maxRank = Math.max(...SOURCES.map((s) => dayData[s]?.length || 0));

  for (let rank = 1; rank <= maxRank; rank++) {
    const row = [rank];
    SOURCES.forEach((source) => {
      const book = dayData[source]?.find((b) => b.rank === rank);
      row.push(book ? `${book.title} / ${book.author}` : "");
    });
    rows.push(row);
  }

  const csv = "\uFEFF" + rows.map((r) => r.map((v) => `"${String(v).replace(/"/g, '""')}"`).join(",")).join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `ebook_ranking_${todayISO}.csv`;
  link.click();
}

prevBtn.addEventListener("click", () => {
  if (dateIndex < AVAILABLE_DATES.length - 1) {
    dateIndex++;
    render();
  }
});
nextBtn.addEventListener("click", () => {
  if (dateIndex > 0) {
    dateIndex--;
    render();
  }
});
document.getElementById("downloadBtn").addEventListener("click", downloadCSV);

render();
