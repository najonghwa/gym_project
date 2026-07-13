// 화면/상호작용 — Tailwind 기반 (shadcn 스타일 다크 테마)
(function () {
  const D = window.DATA, CORE = window.CORE, S = window.STORE, Q = window.QUOTES;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const root = $("#root");

  // 공통 클래스 (NRC 무드: 블랙 + 볼트, 필 버튼, 큰 라운드)
  const CARD = "bg-card border border-white/[0.06] rounded-3xl p-4";
  const BTN = "rounded-full px-4 py-3 font-bold text-[15px] border border-white/15 bg-white/5 text-zinc-100 active:scale-[.97] transition";
  const BTNP = "rounded-full px-4 py-3 font-extrabold text-[15px] bg-pri text-black active:scale-[.97] transition shadow-lg shadow-pri/10";
  const CHIP = "inline-flex items-center rounded-md bg-white/[0.06] border border-white/10 px-2 py-0.5 text-[11px] text-mut";

  let ME = null, USER = null, TAB = "today", SEL_DAY = 1;
  let CAL = new Date(), CAL_SEL = null;
  let RANK_METRIC = "att";
  let BUILDER = null; // 커스텀 루틴 작성 중 상태

  function toast(m) {
    const t = $("#toast"); t.textContent = m; t.classList.remove("hidden");
    clearTimeout(toast._t); toast._t = setTimeout(() => t.classList.add("hidden"), 2200);
  }
  function reload() { USER = S.getUser(ME); }

  // ── 시트(바텀시트) ──
  function openSheet(html, full) {
    $("#sheet-root").innerHTML = `
      <div class="fixed inset-0 z-50 bg-black/70 backdrop-blur-[2px]" data-close></div>
      <div class="fixed left-1/2 -translate-x-1/2 bottom-0 z-[60] w-full max-w-md lg:max-w-lg ${full ? "top-6" : "max-h-[85vh]"}
           bg-card border-t border-x border-white/10 rounded-t-[28px] overflow-y-auto animate-slideUp safe-b">
        <div class="sticky top-0 bg-card/95 backdrop-blur pt-3 pb-1 flex justify-center" data-close>
          <div class="w-10 h-1.5 rounded-full bg-line"></div></div>
        <div class="px-5 pb-8">${html}</div>
      </div>`;
    $$("#sheet-root [data-close]").forEach((el) => el.onclick = closeSheet);
  }
  function closeSheet() { $("#sheet-root").innerHTML = ""; }

  // ═══════════════ 로그인 / 가입 ═══════════════
  let AUTH_MODE = "login"; // login | signup
  function renderLogin() {
    root.innerHTML = `
    <div class="flex flex-col justify-center min-h-screen px-8 max-w-md mx-auto animate-fadeUp">
      <div class="lab mb-3">COMPANY GYM & RUN</div>
      <h1 class="disp text-[52px] leading-[0.95] tracking-tight">오늘도<br><span class="text-pri">한 세트</span> 더.</h1>
      <p class="text-mut mt-4 text-[14px] leading-relaxed">회사 헬스장 맞춤 루틴 · 러닝 플랜 · 기록 · 랭킹</p>
      <div class="w-full grid grid-cols-2 gap-1.5 mt-9 bg-white/[0.06] border border-white/10 rounded-full p-1">
        <button id="md-login" class="rounded-full py-2.5 text-[14px] font-bold ${AUTH_MODE === "login" ? "bg-pri text-black" : "text-mut"}">로그인</button>
        <button id="md-signup" class="rounded-full py-2.5 text-[14px] font-bold ${AUTH_MODE === "signup" ? "bg-pri text-black" : "text-mut"}">처음이에요</button>
      </div>
      <input id="login-id" class="w-full mt-4 bg-card2 border border-white/10 rounded-2xl px-4 py-4 text-center text-base outline-none focus:border-pri" placeholder="아이디 (예: hong)" autocomplete="off" />
      <input id="login-pin" type="password" inputmode="numeric" maxlength="4" class="w-full mt-2.5 bg-card2 border border-white/10 rounded-2xl px-4 py-4 text-center text-base outline-none focus:border-pri tracking-[8px]" placeholder="PIN 4자리" autocomplete="off" />
      <button id="btn-login" class="${BTNP} w-full mt-4 py-4 text-[17px]">${AUTH_MODE === "login" ? "로그인" : "아이디 만들기"}</button>
      <p id="login-msg" class="text-red-400 text-sm mt-3 h-5 text-center"></p>
      <p class="text-mut text-[12px] mt-1 text-center leading-relaxed">${AUTH_MODE === "signup"
        ? "아이디와 4자리 PIN만 정하면 끝! 나중에 다른 폰에서도<br>같은 아이디+PIN으로 로그인하면 기록이 이어져요."
        : "만들어둔 아이디와 PIN을 입력하세요."}</p>
    </div>`;
    const msg = (t, ok) => { const el = $("#login-msg"); el.textContent = t; el.classList.toggle("text-red-400", !ok); el.classList.toggle("text-mut", !!ok); };
    $("#md-login").onclick = () => { AUTH_MODE = "login"; renderLogin(); };
    $("#md-signup").onclick = () => { AUTH_MODE = "signup"; renderLogin(); };

    const go = async () => {
      const id = $("#login-id").value.trim();
      const pin = $("#login-pin").value.trim();
      if (!id) return msg("아이디를 입력하세요.");
      if (!/^\d{4}$/.test(pin)) return msg("PIN은 숫자 4자리예요.");
      const btn = $("#btn-login"); btn.disabled = true;

      if (AUTH_MODE === "signup") {
        // 중복 확인: 이 기기 + 서버 양쪽
        let exists = !!S.getUser(id);
        if (!exists && window.SUPA && SUPA.enabled) {
          msg("아이디 확인 중…", true);
          exists = !!(await SUPA.pullUser(id));
        }
        if (exists) { btn.disabled = false; return msg("이미 사용 중인 아이디예요. 로그인하거나 다른 아이디를 써주세요."); }
        USER = S.login(id); ME = USER.id;
        S.update(ME, { pin });
        reload(); startOnboard(); return;
      }

      // 로그인
      let u = S.getUser(id);
      if (window.SUPA && SUPA.enabled) {
        msg("서버에서 불러오는 중…", true);
        const server = await SUPA.pullUser(id);
        if (server && (server.profile || server.runProfile || server.pin)) { u = S.replaceUser(id, server); }
      }
      if (!u) { btn.disabled = false; return msg("없는 아이디예요. '처음이에요'에서 만들어 주세요."); }
      if (u.pin && u.pin !== pin) { btn.disabled = false; return msg("PIN이 달라요."); }
      USER = S.login(id); ME = USER.id;
      if (!u.pin) S.update(ME, { pin }); // 예전(핀 없던) 계정은 지금 PIN 등록
      reload();
      if (USER.profile && USER.routine) renderMain(); else startOnboard();
    };
    $("#btn-login").onclick = go;
    $("#login-pin").addEventListener("keydown", (e) => { if (e.key === "Enter") go(); });
  }

  // ═══════════════ 온보딩 ═══════════════
  const CAREER = [
    { v: 1, t: "이제 시작", d: "3개월 미만" }, { v: 4, t: "몇 달 됨", d: "3~6개월" },
    { v: 9, t: "반년~1년", d: "6개월~1년" }, { v: 18, t: "1~2년", d: "꾸준히 1~2년" },
    { v: 36, t: "2년 이상", d: "베테랑" },
  ];
  const FOCUS = [
    { v: "full", em: "⚖️", t: "전신 균형", d: "골고루" },
    { v: "upper", em: "👕", t: "상체 위주", d: "가슴·등·어깨·팔" },
    { v: "lower", em: "🦵", t: "하체 위주", d: "다리·엉덩이" },
    { v: "core", em: "🧱", t: "코어 강화", d: "복근·허리" },
  ];
  const DAYS = [2, 3, 4, 5, 6].map((v) => ({ v, t: "주 " + v + "회" }));
  const TIMES = [
    { v: 30, t: "30분", d: "짧고 굵게" }, { v: 45, t: "45분", d: "적당히" },
    { v: 60, t: "60분", d: "표준" }, { v: 90, t: "90분", d: "여유롭게" },
  ];
  const DURATIONS = [
    { v: 4, t: "4주 프로젝트", d: "짧고 굵게 몸 깨우기" },
    { v: 8, t: "8주 프로젝트", d: "눈에 띄는 변화 (추천)" },
    { v: 12, t: "12주 프로젝트", d: "확실한 몸 변화" },
    { v: 0, t: "기간 없이 계속", d: "습관으로 쭉" },
  ];
  const STEPS = ["basic", "career", "style", "days", "time", "duration", "focus", "confirm"];
  const KEYMAP = { career: "months", style: "style", days: "days", time: "sessionMin", duration: "programWeeks", focus: "focus" };
  let STEP = 0, A = {}, OB_STEPS = STEPS;

  function startOnboard() {
    STEP = 0;
    const has = USER.profile && USER.profile.height; // 개인정보는 처음 한 번만 — 이후엔 설정에서
    A = USER.profile ? Object.assign({ programWeeks: 8 }, USER.profile)
      : { sex: "male", age: 30, height: 172, weight: 0, months: 1, style: null, days: 3, sessionMin: 60, programWeeks: 8, focus: "full", split: null };
    OB_STEPS = has ? STEPS.filter((s) => s !== "basic") : STEPS;
    renderOb();
  }

  function opt(sel, dataAttr, val, inner, extra) {
    return `<div class="rounded-2xl border ${sel ? "border-pri bg-pri/10" : "border-line bg-card2"} p-4 cursor-pointer active:scale-[.99] transition ${extra || ""}" data-${dataAttr}="${val}">${inner}</div>`;
  }

  function renderOb() {
    const key = OB_STEPS[STEP];
    let body = "";
    if (key === "basic") {
      body = `<h2 class="text-xl font-extrabold mb-5">기본 정보를 알려주세요</h2>
        <div class="grid grid-cols-2 gap-2.5 mb-4">
          ${opt(A.sex === "male", "sex", "male", `<div class="text-center font-bold">🙋‍♂️ 남성</div>`)}
          ${opt(A.sex === "female", "sex", "female", `<div class="text-center font-bold">🙋‍♀️ 여성</div>`)}
        </div>
        ${numField("age", "나이", A.age, "세")}${numField("height", "키", A.height, "cm")}${numField("weight", "몸무게 (선택)", A.weight > 0 ? A.weight : "", "kg", "비워도 돼요")}
        <p class="text-mut text-[12.5px] mt-3 leading-relaxed">몸무게는 소모 칼로리 예측에만 쓰여요. <b>비워두면 평균값으로 대충 계산</b>하니 입력하기 싫으면 건너뛰세요.</p>`;
    } else if (key === "career") {
      body = `<h2 class="text-xl font-extrabold mb-5">운동 경력은 어느 정도세요?</h2><div class="space-y-2.5">` +
        CAREER.map((o) => opt(A.months === o.v, "v", o.v,
          `<div class="font-bold">${o.t}</div><div class="text-mut text-[13px] mt-0.5">${o.d}</div>`)).join("") + `</div>`;
    } else if (key === "style") {
      body = `<h2 class="text-xl font-extrabold mb-5">어떤 몸을 목표로 하세요?</h2><div class="space-y-2.5">` +
        D.STYLES.map((s) => opt(A.style === s.id, "v", s.id,
          `<div class="flex items-center gap-3.5"><div class="text-[26px]">${s.emoji}</div>
           <div><div class="font-bold">${esc(s.name)}</div><div class="text-mut text-[13px] mt-0.5">${esc(s.easy)}</div></div></div>`)).join("") + `</div>`;
    } else if (key === "days") {
      body = `<h2 class="text-xl font-extrabold mb-5">일주일에 몇 번 오실 수 있나요?</h2><div class="grid grid-cols-2 gap-2.5">` +
        DAYS.map((o) => opt(A.days === o.v, "v", o.v, `<div class="text-center font-bold">${o.t}</div>`)).join("") + `</div>`;
    } else if (key === "time") {
      body = `<h2 class="text-xl font-extrabold mb-5">한 번 오면 보통 얼마나 하세요?</h2><div class="grid grid-cols-2 gap-2.5">` +
        TIMES.map((o) => opt(A.sessionMin === o.v, "v", o.v,
          `<div class="text-center font-bold">${o.t}</div><div class="text-center text-mut text-[12px] mt-0.5">${o.d}</div>`)).join("") + `</div>
        <p class="text-mut text-[12.5px] mt-4">시간에 맞춰 하루 운동 개수를 자동으로 조절해 드려요.</p>`;
    } else if (key === "duration") {
      body = `<h2 class="text-xl font-extrabold mb-5">몇 주 프로젝트로 갈까요?</h2><div class="space-y-2.5">` +
        DURATIONS.map((o) => opt(A.programWeeks === o.v, "v", o.v,
          `<div class="font-bold">${o.t}</div><div class="text-mut text-[13px] mt-0.5">${o.d}</div>`)).join("") + `</div>
        <p class="text-mut text-[12.5px] mt-4">기간이 끝나면 다시 진단해서 다음 단계 루틴으로 올라가는 걸 추천해요.</p>`;
    } else if (key === "focus") {
      body = `<h2 class="text-xl font-extrabold mb-5">특별히 신경 쓰고 싶은 곳이 있나요?</h2><div class="space-y-2.5">` +
        FOCUS.map((o) => opt(A.focus === o.v, "v", o.v,
          `<div class="flex items-center gap-3.5"><div class="text-[24px]">${o.em}</div>
           <div><div class="font-bold">${o.t}</div><div class="text-mut text-[13px]">${o.d}</div></div></div>`)).join("") + `</div>`;
    } else {
      const level = D.levelFromMonths(A.months);
      const reco = CORE.recommendSplit(+A.days, level);
      if (!A.split) A.split = reco;
      const st = D.STYLE_BY_ID[A.style] || D.STYLES[0];
      body = `<h2 class="text-xl font-extrabold mb-4">이렇게 준비했어요 ✨</h2>
        <div class="rounded-2xl border border-pri/60 bg-pri/10 p-4 text-[14px] leading-relaxed">
          <b>${st.emoji} ${esc(st.name)}</b> · ${D.LEVEL_KR[level]} · 주 ${A.days}회 · 회당 ${A.sessionMin}분<br>
          <span class="text-mut">${esc(st.long)}</span></div>
        <h3 class="font-extrabold mt-6 mb-3">추천 분할</h3><div class="space-y-2.5">` +
        Object.keys(D.SPLITS).map((sid) => {
          const sp = D.SPLITS[sid];
          return opt(A.split === sid, "split", sid,
            `<div class="font-bold">${esc(sp.name)} ${sid === reco ? '<span class="ml-1 text-[10px] font-extrabold bg-gold text-amber-950 rounded px-1.5 py-0.5 align-middle">추천</span>' : ""}</div>
             <div class="text-mut text-[12.5px] mt-1 leading-relaxed">${esc(sp.easy)} — ${esc(sp.long)}</div>`);
        }).join("") + `</div>`;
    }

    root.innerHTML = `
    <div class="px-5 pt-5 pb-32 animate-fadeUp">
      <div class="flex items-center gap-3 mb-6">
        <div class="flex-1 h-2 bg-card2 rounded-full overflow-hidden">
          <div class="h-full bg-gradient-to-r from-pri to-pri2 transition-all" style="width:${(STEP + 1) / OB_STEPS.length * 100}%"></div></div>
        <span class="text-mut text-xs font-bold">${STEP + 1}/${OB_STEPS.length}</span></div>
      ${body}
    </div>
    <div class="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md flex gap-2.5 px-5 pb-6 pt-8 bg-gradient-to-t from-base via-base/95 to-transparent">
      <button id="ob-prev" class="${BTN} flex-1 ${STEP === 0 ? "invisible" : ""}">이전</button>
      <button id="ob-next" class="${BTNP} flex-[2]">${STEP === OB_STEPS.length - 1 ? "루틴 만들기 💪" : "다음"}</button>
    </div>`;

    $$("[data-sex]").forEach((el) => el.onclick = () => { A.sex = el.dataset.sex; renderOb(); });
    $$("[data-v]").forEach((el) => el.onclick = () => {
      const raw = el.dataset.v;
      A[KEYMAP[OB_STEPS[STEP]]] = isNaN(+raw) ? raw : +raw; renderOb();
    });
    $$("[data-split]").forEach((el) => el.onclick = () => { A.split = el.dataset.split; renderOb(); });
    $$("[data-num]").forEach((el) => el.oninput = () => { A[el.dataset.num] = parseFloat(el.value) || 0; });
    $("#ob-prev").onclick = () => { if (STEP > 0) { STEP--; renderOb(); } };
    $("#ob-next").onclick = () => {
      const key = OB_STEPS[STEP];
      if (key === "career" && A.months == null) return toast("하나 골라주세요");
      if (key === "style" && !A.style) return toast("목표를 골라주세요");
      if (STEP < OB_STEPS.length - 1) { STEP++; renderOb(); return; }
      const level = D.levelFromMonths(A.months);
      const profile = Object.assign({}, A, { level });
      const routine = CORE.buildRoutine(profile);
      routine.programWeeks = profile.programWeeks || 0;  // 0=기간 없이
      routine.startDate = S.today();
      S.update(ME, { profile, routine });
      reload(); TAB = "today"; renderMain();
      toast("맞춤 루틴 완성! 💪");
    };
  }
  function numField(key, label, val, unit, ph) {
    return `<div class="mb-3"><label class="text-mut text-[13px] block mb-1.5">${label}</label>
      <div class="flex items-center gap-2">
        <input class="flex-1 bg-card2 border border-line rounded-xl px-4 py-3.5 outline-none focus:border-pri placeholder:text-zinc-600" type="number" inputmode="numeric" data-num="${key}" value="${val}" placeholder="${ph || ""}" />
        <span class="text-mut w-8">${unit}</span></div></div>`;
  }

  // ═══════════════ 메인 셸 ═══════════════
  const NAV = [
    { id: "today", em: "🏋️", t: "오늘" }, { id: "run", em: "🏃", t: "러닝" },
    { id: "calendar", em: "📅", t: "달력" }, { id: "stats", em: "📊", t: "분석" },
    { id: "routine", em: "📋", t: "루틴" }, { id: "ranking", em: "🏆", t: "랭킹" },
    { id: "gym", em: "🗺️", t: "헬스장" },
  ];
  function renderMain() {
    reload();
    const st = S.stats(USER);
    root.innerHTML = `
    <header class="sticky top-0 z-30 bg-base/90 backdrop-blur border-b border-line/60">
      <div class="px-5 py-3 flex items-center justify-between lg:max-w-6xl lg:mx-auto lg:px-8">
        <div class="disp text-[17px] tracking-tight">GYM<span class="text-pri">&</span>RUN <span class="text-[11px] text-mut font-sans font-bold align-middle ml-0.5">헬스 가이드</span></div>
        <button id="btn-me" class="flex items-center gap-2 bg-card2 border border-line rounded-full pl-3 pr-1.5 py-1.5 active:scale-95 transition">
          <span class="text-[12px] font-bold">${esc(USER.id)}</span>
          <span class="w-7 h-7 rounded-full bg-gradient-to-br from-amber-400 to-amber-600 text-amber-950 text-[11px] font-extrabold flex items-center justify-center">Lv${st.level}</span>
        </button>
      </div>
    </header>
    <div class="lg:flex lg:gap-8 lg:max-w-6xl lg:mx-auto lg:px-8 lg:pt-6">
      <nav class="hidden lg:flex lg:flex-col gap-1.5 w-48 shrink-0 sticky top-20 self-start">
        ${NAV.map((n) => `
          <button class="flex items-center gap-3 rounded-xl px-4 py-3 text-[14.5px] font-bold text-left transition
            ${TAB === n.id ? "bg-pri text-black" : "text-mut hover:bg-card2"}" data-tab="${n.id}">
            <span class="text-[19px]">${n.em}</span>${n.t}</button>`).join("")}
      </nav>
      <main id="pane" class="flex-1 min-w-0 px-4 pt-3 pb-32 animate-fadeUp lg:px-0 lg:pt-0 lg:pb-16 lg:columns-2 lg:gap-5"></main>
    </div>
    <nav class="lg:hidden fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md bg-black/90 backdrop-blur-xl border-t border-white/10 flex safe-b z-30">
      ${NAV.map((n) => `
        <button class="flex-1 py-2.5 flex flex-col items-center gap-0.5 min-w-0 ${TAB === n.id ? "text-pri" : "text-zinc-600"}" data-tab="${n.id}">
          <span class="text-[18px] leading-none ${TAB === n.id ? "" : "grayscale opacity-70"}">${n.em}</span>
          <span class="text-[9.5px] font-bold">${n.t}</span>
          <span class="w-1 h-1 rounded-full ${TAB === n.id ? "bg-pri" : "bg-transparent"}"></span>
        </button>`).join("")}
    </nav>`;
    $("#btn-me").onclick = openMe;
    $$("[data-tab]").forEach((b) => b.onclick = () => { TAB = b.dataset.tab; renderMain(); });
    const pane = $("#pane");
    if (TAB === "today") viewToday(pane);
    if (TAB === "run") viewRun(pane);
    if (TAB === "calendar") viewCalendar(pane);
    if (TAB === "stats") viewStats(pane);
    if (TAB === "routine") viewRoutine(pane);
    if (TAB === "ranking") viewRanking(pane);
    if (TAB === "gym") viewGym(pane);
  }

  // ═══════════════ 오늘 ═══════════════
  function recommendedDay() {
    const wk = USER.routine.week;
    const n = Object.values(USER.workouts || {}).filter((w) => (w.doneSets || 0) > 0).length;
    return (n % wk.length) + 1;
  }
  const todayWorkout = () => (USER.workouts || {})[S.today()] || null;

  function viewToday(pane) {
    const st = S.stats(USER), routine = USER.routine;
    const tw = todayWorkout();
    SEL_DAY = tw ? tw.day : recommendedDay();
    const day = routine.week.find((d) => d.day === SEL_DAY) || routine.week[0];
    const items = (tw && tw.items) ? tw.items : day.items;  // 오늘만 커스텀했으면 그걸 사용
    const doneMap = tw ? tw.sets : {};
    const score = CORE.sessionScore(items, doneMap);
    const q = Q.pick(S.today(), USER.id);
    const prog = programProgress(routine);

    // 데스크탑(lg)은 위젯 대시보드로
    if (window.matchMedia && matchMedia("(min-width:1024px)").matches) {
      return renderDashboard(pane, { st, routine, day, items, doneMap, score, q, prog, tw });
    }

    pane.innerHTML = `
    <div class="${CARD} mb-3">
      <div class="flex items-end justify-between">
        <div>
          <div class="lab mb-1">연속 운동 STREAK</div>
          <div class="flex items-end gap-2">
            <span class="disp text-[64px] leading-[0.85] ${st.streak > 0 ? "text-pri" : "text-zinc-700"}">${st.streak}</span>
            <span class="pb-1 text-mut font-bold text-[14px]">일째 🔥</span></div></div>
        <div class="text-right pb-1">
          <div class="text-[11.5px] text-mut">다음 레벨까지 <b class="text-zinc-100">${st.toNext}</b> XP</div>
          <div class="w-28 h-1.5 bg-white/10 rounded-full overflow-hidden mt-1.5 ml-auto">
            <div class="h-full bg-pri" style="width:${st.progressPct}%"></div></div></div></div>
      <div class="grid grid-cols-4 gap-2 mt-5">
        ${[["총 운동", st.sessions], ["소모 kcal", st.totalKcal.toLocaleString()], ["최고연속", st.best], ["뱃지", st.badges.length]]
          .map(([l, n]) => `<div class="bg-white/[0.05] rounded-2xl py-2.5 text-center">
            <div class="disp text-[19px] leading-none">${n}</div><div class="text-[10px] text-mut mt-1">${l}</div></div>`).join("")}
      </div>
      ${prog ? `<div class="mt-3">
        <div class="flex justify-between text-[11.5px] text-mut mb-1">
          <span>${prog.done ? "🎉 프로그램 완료! '다시 진단'으로 다음 단계 가요" : `📆 ${prog.total}주 프로젝트 · ${prog.week}주차`}</span>
          <span>${prog.pct}%</span></div>
        <div class="h-1.5 bg-black/40 rounded-full overflow-hidden">
          <div class="h-full ${prog.done ? "bg-gold" : "bg-sky-500"}" style="width:${prog.pct}%"></div></div>
      </div>` : ""}</div>

    <div class="${CARD} mb-3 border-l-4 border-l-gold">
      <div class="text-[14.5px] leading-relaxed font-medium">💬 ${esc(q.main)}</div>
      <div class="text-mut text-[12px] mt-1.5">${esc(q.tail)}</div></div>

    <div class="${CARD}">
      <div class="flex items-center justify-between mb-3">
        <div><h2 class="text-lg font-extrabold">오늘의 운동</h2>
          <div class="text-mut text-[13px]">${esc(day.typeKr)}</div></div>
        <div class="ring w-[74px] h-[74px]" style="--p:${score.pct}"><b class="text-[17px] font-extrabold">${score.pct}%</b></div></div>
      <div class="flex gap-2 overflow-x-auto pb-2 mb-1">
        ${routine.week.map((d) => {
          const on = d.day === SEL_DAY, reco = d.day === recommendedDay();
          return `<button class="shrink-0 rounded-lg px-3.5 py-2 text-[13px] font-bold border ${on ? "bg-pri text-black border-pri" : reco ? "border-gold text-zinc-100 bg-card2" : "border-line text-zinc-300 bg-card2"}" data-day="${d.day}">Day ${d.day}</button>`;
        }).join("")}</div>
      <div id="exlist">${items.map((it) => exCard(it, doneMap[it.exId] || 0, tw && tw.weights ? tw.weights[it.exId] : null)).join("")}</div>
      <button id="today-add" class="${BTN} w-full !py-2.5 mt-1 text-[13.5px]">➕ 오늘 운동 추가</button>
      <p class="text-mut text-[12px] leading-relaxed mt-3">운동 이름을 누르면 <b>동작·자극부위</b>가 나와요. ⋯ 로 오늘만 교체·삭제·세트 조절. Day는 순환 — 마지막 Day 다음엔 다시 Day 1! 🎁</p>
    </div>`;

    bindToday(pane, routine, items);
  }

  // 오늘 운동 공용 바인딩 (모바일/대시보드 공용)
  function bindToday(pane, routine, items) {
    $$("[data-day]", pane).forEach((b) => b.onclick = () => {
      const tw2 = todayWorkout(); SEL_DAY = +b.dataset.day;
      if (tw2) {
        const nd = routine.week.find((d) => d.day === SEL_DAY) || routine.week[0];
        if (tw2.items) tw2.items = JSON.parse(JSON.stringify(nd.items)); // Day 바꾸면 그 Day 기준으로
        S.saveWorkout(ME, S.today(), recompute(SEL_DAY, tw2.sets, tw2.items || nd.items));
        reload();
      }
      viewToday(pane);
    });
    bindSets(pane, items);
    const add = $("#today-add", pane); if (add) add.onclick = () => openTodayPicker(pane);
    $$("#exlist [data-info]", pane).forEach((el) => el.onclick = () => openExercise(el.dataset.info));
    $$("#exlist [data-menu]", pane).forEach((el) => el.onclick = (e) => { e.stopPropagation(); openExMenu(pane, el.dataset.menu); });
  }

  // ═══════════════ 데스크탑 대시보드 (오늘 탭, lg 이상) ═══════════════
  function renderDashboard(pane, ctx) {
    const { st, routine, day, items, doneMap, score, q, prog, tw } = ctx;
    pane.classList.remove("lg:columns-2");   // 대시보드는 컬럼 대신 그리드
    const w = USER.workouts || {}, runs = USER.runs || [];
    const rst = R.stats(runs);
    const ws = USER.runPlan ? R.weekScore(USER.runPlan, runs) : null;

    // 미니 달력 (이번 달)
    const now = new Date(), y = now.getFullYear(), m = now.getMonth();
    const startDow = new Date(y, m, 1).getDay(), daysIn = new Date(y, m + 1, 0).getDate();
    const runsBy = {}; runs.forEach((r) => { runsBy[r.date] = true; });
    let mini = ["일", "월", "화", "수", "목", "금", "토"].map((x) => `<div class="text-center text-[9px] text-zinc-600 py-0.5">${x}</div>`).join("");
    for (let i = 0; i < startDow; i++) mini += `<div></div>`;
    for (let d = 1; d <= daysIn; d++) {
      const k = S.fmt(new Date(y, m, d));
      const g = w[k] && (w[k].doneSets || 0) > 0, r = !!runsBy[k];
      mini += `<div class="aspect-square rounded-md flex flex-col items-center justify-center text-[9.5px]
        ${g && w[k].scorePct >= 100 ? "bg-pri/20 text-pri font-bold" : g ? "bg-amber-900/40 text-gold font-bold" : r ? "bg-sky-900/40 text-sky-400 font-bold" : "bg-white/[0.04] text-zinc-600"}
        ${k === S.today() ? "ring-1 ring-gold" : ""}">${d}${r && g ? "•" : ""}</div>`;
    }

    // 차트 데이터
    const days14 = lastDays(14);
    const kcalData = days14.map((d) => ({ l: d.l.slice(d.l.indexOf("/") + 1), v: w[d.key] ? Math.round(w[d.key].kcal || 0) : 0 }));
    const paceData = runs.slice(-14).map((r) => ({ l: r.date.slice(5), sec: r.paceSec }));

    // 최고 중량 top5
    const bw = {};
    Object.keys(w).sort().forEach((d) => { const wgt = w[d].weights || {}; Object.keys(wgt).forEach((ex) => {
      const cur = bw[ex] || (bw[ex] = { best: 0 }); if (wgt[ex] > cur.best) cur.best = wgt[ex]; }); });
    const bwTop = Object.keys(bw).map((ex) => ({ ex, best: bw[ex].best })).sort((a, b) => b.best - a.best).slice(0, 5);

    // 랭킹 top5 + 나
    const met = (r) => r.att || 0;
    const rows = S.ranking().sort((a, b) => met(b) - met(a)).slice(0, 5);

    // 3대
    const b3 = USER.big3;
    const b3last = b3 && b3.logs && b3.logs.length ? b3.logs[b3.logs.length - 1] : null;
    const b3total = b3last ? Math.round((b3last.s + b3last.b + b3last.d) * 10) / 10 : 0;
    const b3pct = b3last ? Math.min(100, Math.round(b3total / b3.goal * 100)) : 0;

    // KPI: 이번 주 헬스 세션 수 (지난주 대비 델타) + 4주 출석률
    const wk2 = lastWeeks(2);
    const cntIn = (wb) => Object.keys(w).filter((k) => {
      const d = new Date(k + "T00:00:00"); return d >= wb.st && d < wb.en && (w[k].doneSets || 0) > 0;
    }).length;
    const thisWCnt = cntIn(wk2[1]), lastWCnt = cntIn(wk2[0]);
    const cons = S.consistency28(USER, routine.days);

    // 부위별 볼륨 (최근 7일 완료 세트 집계)
    const vol = {};
    const cut7 = new Date(); cut7.setDate(cut7.getDate() - 6); cut7.setHours(0, 0, 0, 0);
    Object.keys(w).forEach((k) => {
      if (new Date(k + "T00:00:00") < cut7) return;
      const sets = w[k].sets || {};
      Object.keys(sets).forEach((exId) => {
        const ex = D.byId(exId); const n = sets[exId];
        if (ex && n) { const m = ex.primary[0]; vol[m] = (vol[m] || 0) + n; }
      });
    });
    const volList = Object.keys(vol).map((m) => ({ m, n: vol[m] })).sort((a, b) => b.n - a.n).slice(0, 6);
    const volMax = Math.max(...volList.map((v) => v.n), 1);

    // KPI 타일 (좌측 상태색 바 — cphf 대시보드 스타일)
    const kpi = (label, value, unit, sub, color, delta) => `
      <div class="relative overflow-hidden rounded-2xl bg-white/[0.04] border border-white/[0.06] px-3.5 py-2.5">
        <span class="absolute left-0 top-0 h-full w-1 ${color}"></span>
        <div class="pl-1.5">
          <div class="text-[10.5px] text-mut font-bold">${label}</div>
          <div class="mt-0.5 flex items-baseline gap-1">
            <span class="disp text-[22px] leading-none tabular-nums">${value}</span>
            ${unit ? `<span class="text-[11px] text-mut">${unit}</span>` : ""}
            ${delta != null && delta !== 0 ? `<span class="ml-1 text-[11px] font-bold ${delta > 0 ? "text-pri" : "text-red-400"}">${delta > 0 ? "▲" : "▼"}${Math.abs(delta)}</span>` : ""}</div>
          ${sub ? `<div class="mt-0.5 text-[10.5px] text-zinc-500 truncate">${sub}</div>` : ""}</div></div>`;

    const W = (span, inner, extra) => `<div class="${CARD} col-span-12 ${span} ${extra || ""}">${inner}</div>`;

    pane.innerHTML = `
    <div class="flex items-center justify-between mb-4">
      <div><div class="lab">DASHBOARD</div>
        <h2 class="disp text-[28px] leading-tight">${esc(USER.id)}<span class="text-pri">.</span> 오늘도 갑시다</h2></div>
      <div class="text-right text-[12px] text-mut">${S.today()} · ${esc(routine.summary)}</div></div>
    <div class="grid grid-cols-12 gap-4 auto-rows-min">

      <div class="col-span-12 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
        ${kpi("오늘 달성률", score.pct, "%", esc(day.typeKr), score.pct >= 100 ? "bg-pri" : score.pct > 0 ? "bg-gold" : "bg-zinc-700")}
        ${kpi("연속 운동", st.streak, "일", "최고 " + st.best + "일", st.streak > 0 ? "bg-pri" : "bg-zinc-700")}
        ${kpi("이번 주 헬스", thisWCnt, "회", "목표 주 " + routine.days + "회", thisWCnt >= routine.days ? "bg-pri" : "bg-gold", thisWCnt - lastWCnt)}
        ${kpi("이번 주 러닝", ws ? ws.doneKm : 0, "km", ws ? "목표 " + ws.targetKm + "km" : "플랜 없음", ws && ws.pct >= 100 ? "bg-pri" : "bg-sky-500")}
        ${kpi("3대 합계", b3last ? b3total : "—", b3last ? "kg" : "", b3last ? "목표 " + b3.goal + "kg" : "미도전", b3last ? "bg-gold" : "bg-zinc-700")}
        ${kpi("4주 출석률", cons.pct, "%", cons.done + "/" + cons.planned + "회", cons.pct >= 80 ? "bg-pri" : cons.pct >= 50 ? "bg-gold" : "bg-red-500")}
      </div>

      ${W("lg:col-span-3", `
        <div class="lab mb-1">연속 STREAK</div>
        <div class="flex items-end gap-1.5">
          <span class="disp text-[52px] leading-[0.85] ${st.streak > 0 ? "text-pri" : "text-zinc-700"}">${st.streak}</span>
          <span class="pb-1 text-mut font-bold text-[13px]">일 🔥</span></div>
        <div class="grid grid-cols-2 gap-1.5 mt-4">
          ${[["총 운동", st.sessions], ["kcal", st.totalKcal.toLocaleString()], ["최고연속", st.best], ["Lv", st.level]]
            .map(([l, n]) => `<div class="bg-white/[0.05] rounded-xl py-2 text-center">
              <div class="disp text-[16px] leading-none">${n}</div><div class="text-[9.5px] text-mut mt-0.5">${l}</div></div>`).join("")}</div>
        ${prog ? `<div class="mt-3"><div class="flex justify-between text-[10.5px] text-mut mb-1">
          <span>📆 ${prog.total}주 · ${prog.week}주차</span><span>${prog.pct}%</span></div>
          <div class="h-1 bg-white/10 rounded-full"><div class="h-full ${prog.done ? "bg-gold" : "bg-sky-500"} rounded-full" style="width:${prog.pct}%"></div></div></div>` : ""}`)}

      ${W("lg:col-span-3", ws ? `
        <div class="lab mb-1">이번 주 러닝</div>
        <div class="flex items-end gap-1.5">
          <span class="disp text-[52px] leading-[0.85]">${ws.doneKm}</span>
          <span class="pb-1 text-mut font-bold text-[13px]">/ ${ws.targetKm}km</span></div>
        <div class="h-2 bg-white/10 rounded-full overflow-hidden mt-3">
          <div class="h-full bg-sky-400 rounded-full" style="width:${ws.pct}%"></div></div>
        <div class="grid grid-cols-2 gap-1.5 mt-3">
          ${[["이번달", rst.monthKm + "km"], ["최고페이스", R.paceStr(rst.bestPace)]]
            .map(([l, v]) => `<div class="bg-white/[0.05] rounded-xl py-2 text-center">
              <div class="disp text-[14px] leading-none">${v}</div><div class="text-[9.5px] text-mut mt-0.5">${l}</div></div>`).join("")}</div>
        <button class="${BTN} w-full !py-2 !text-[12px] mt-3" data-goto="run">기록 입력 →</button>`
        : `<div class="lab mb-1">러닝</div><p class="text-mut text-[12.5px] mt-2 leading-relaxed">아직 러닝 플랜이 없어요.<br>성향 진단으로 시작해 보세요!</p>
           <button class="${BTNP} w-full !py-2.5 mt-4" data-goto="run">러닝 시작 🏃</button>`)}

      ${W("lg:col-span-3", `
        <div class="flex items-center justify-between"><div class="lab">3대 챌린지</div>
          <button class="text-[11px] text-mut font-bold" data-goto="stats">관리 →</button></div>
        ${b3last ? `
        <div class="flex items-end gap-1.5 mt-1">
          <span class="disp text-[52px] leading-[0.85] text-gold">${b3total}</span>
          <span class="pb-1 text-mut font-bold text-[13px]">/ ${b3.goal}kg</span></div>
        <div class="h-2 bg-white/10 rounded-full overflow-hidden mt-3">
          <div class="h-full bg-gradient-to-r from-amber-500 to-amber-300 rounded-full" style="width:${b3pct}%"></div></div>
        <div class="grid grid-cols-3 gap-1.5 mt-3">
          ${[["SQ", b3last.s], ["BP", b3last.b], ["DL", b3last.d]].map(([l, v]) =>
            `<div class="bg-white/[0.05] rounded-xl py-2 text-center">
              <div class="disp text-[15px] leading-none">${v}</div><div class="text-[9.5px] text-mut mt-0.5">${l}</div></div>`).join("")}</div>`
        : `<p class="text-mut text-[12.5px] mt-2 leading-relaxed">스쿼트+벤치+데드 합계 도전.<br>3대 300부터 시작해 볼까요?</p>
           <button class="${BTNP} w-full !py-2.5 mt-4" data-goto="stats">도전 시작 🏆</button>`}`)}

      ${W("lg:col-span-3", `
        <div class="lab mb-2">오늘의 한마디</div>
        <div class="text-[14px] leading-relaxed font-medium">💬 ${esc(q.main)}</div>
        <div class="text-mut text-[11.5px] mt-2">${esc(q.tail)}</div>
        <div class="mt-3 pt-3 border-t border-white/[0.06] flex items-center justify-between">
          <span class="text-[11px] text-mut">🏅 뱃지 ${st.badges.length}/${st.badgeDefs.length}</span>
          <span class="text-[11px] text-mut">XP ${st.xp.toLocaleString()}</span></div>`)}

      ${W("lg:col-span-5 lg:row-span-2", `
        <div class="flex items-center justify-between mb-3">
          <div><div class="lab">오늘의 운동 TODAY</div>
            <h3 class="font-extrabold text-[16px]">${esc(day.typeKr)}</h3></div>
          <div class="ring w-[64px] h-[64px]" style="--p:${score.pct}"><b class="text-[15px] font-extrabold">${score.pct}%</b></div></div>
        <div class="flex gap-1.5 overflow-x-auto pb-2">
          ${routine.week.map((d) => {
            const on = d.day === SEL_DAY, reco = d.day === recommendedDay();
            return `<button class="shrink-0 rounded-full px-3 py-1.5 text-[12px] font-bold border ${on ? "bg-pri text-black border-pri" : reco ? "border-gold text-zinc-100 bg-card2" : "border-white/10 text-zinc-400 bg-card2"}" data-day="${d.day}">Day ${d.day}</button>`;
          }).join("")}</div>
        <div id="exlist" class="max-h-[520px] overflow-y-auto pr-1">${items.map((it) => exCard(it, doneMap[it.exId] || 0, tw && tw.weights ? tw.weights[it.exId] : null)).join("")}</div>
        <button id="today-add" class="${BTN} w-full !py-2 mt-1 text-[12.5px]">➕ 오늘 운동 추가</button>`)}

      ${W("lg:col-span-4", `
        <div class="flex items-center justify-between mb-2"><div class="lab">${y}년 ${m + 1}월</div>
          <button class="text-[11px] text-mut font-bold" data-goto="calendar">달력 →</button></div>
        <div class="grid grid-cols-7 gap-1">${mini}</div>`)}

      ${W("lg:col-span-3", `
        <div class="flex items-center justify-between mb-2"><div class="lab">출석률 랭킹</div>
          <button class="text-[11px] text-mut font-bold" data-goto="ranking">전체 →</button></div>
        ${rows.map((r, i) => {
          const isMe = !r.demo && r.id.toLowerCase() === USER.id.toLowerCase();
          return `<div class="flex items-center gap-2 py-1.5 ${isMe ? "text-pri" : ""}">
            <span class="w-5 text-[12px] font-extrabold">${["🥇", "🥈", "🥉"][i] || (i + 1)}</span>
            <span class="flex-1 text-[12.5px] font-bold truncate">${esc(r.id)}</span>
            <b class="text-[12.5px]">${r.att || 0}%</b></div>`;
        }).join("")}`)}

      ${W("lg:col-span-4", `
        <div class="lab mb-1">일별 소모 KCAL · 14일</div>${barChart(kcalData, "#ccff00", "")}`)}

      ${W("lg:col-span-3", `
        <div class="flex items-center justify-between mb-1"><div class="lab">최고 중량 TOP5</div>
          <button class="text-[11px] text-mut font-bold" data-goto="stats">전체 →</button></div>
        ${bwTop.length ? bwTop.map((r) => {
          const ex = D.byId(r.ex);
          return `<div class="flex justify-between py-1.5 text-[12.5px]">
            <span class="truncate">${ex ? (ex.em || "") + " " + esc(ex.name) : r.ex}</span>
            <b class="text-gold shrink-0 ml-2">${r.best}kg</b></div>`;
        }).join("") : `<p class="text-mut text-[12px] mt-2 leading-relaxed">⋯ 메뉴에서 중량을 기록하면<br>여기 TOP5가 쌓여요.</p>`}`)}

      ${W("lg:col-span-4", `
        <div class="lab mb-1">페이스 추이</div>${paceChart(paceData)}`)}

      ${W("lg:col-span-4", `
        <div class="lab mb-2">부위별 볼륨 · 최근 7일</div>
        ${volList.length ? volList.map((v) => `
          <div class="flex items-center gap-2 py-1">
            <span class="w-14 text-[11px] text-mut font-bold shrink-0">${D.MUSCLE_KR[v.m]}</span>
            <div class="flex-1 h-3 bg-white/[0.06] rounded-full overflow-hidden">
              <div class="h-full bg-pri rounded-full" style="width:${Math.round(v.n / volMax * 100)}%"></div></div>
            <b class="w-10 text-right text-[11.5px]">${v.n}<span class="text-[9px] text-mut">set</span></b></div>`).join("")
          : `<p class="text-mut text-[12px] mt-2 leading-relaxed">이번 주 세트를 체크하면<br>부위 밸런스가 여기 보여요.</p>`}`)}

      ${W("lg:col-span-4", `
        <div class="lab mb-2">빠른 이동</div>
        <div class="grid grid-cols-2 gap-2">
          ${[["routine", "📋", "루틴 관리"], ["gym", "🗺️", "평면도"], ["stats", "📊", "분석"], ["run", "🏃", "러닝"]]
            .map(([id, em, t]) => `<button class="bg-white/[0.05] hover:bg-white/[0.1] rounded-xl py-3 text-center transition" data-goto="${id}">
              <div class="text-[18px]">${em}</div><div class="text-[10.5px] text-mut mt-1 font-bold">${t}</div></button>`).join("")}</div>`)}
    </div>`;

    bindToday(pane, routine, items);
    $$("[data-goto]", pane).forEach((b) => b.onclick = () => { TAB = b.dataset.goto; renderMain(); });
  }

  // 프로그램 기간 진행률 (기간 없으면 null)
  function programProgress(routine) {
    if (!routine.programWeeks || !routine.startDate) return null;
    const start = new Date(routine.startDate + "T00:00:00");
    const days = Math.max(0, Math.floor((new Date() - start) / 86400000));
    const total = routine.programWeeks;
    const week = Math.min(total, Math.floor(days / 7) + 1);
    const pct = Math.min(100, Math.round(days / (total * 7) * 100));
    return { week, total, pct, done: pct >= 100 };
  }

  function exCard(it, done, wNow) {
    const total = it.sets;
    const full = done >= total && total > 0;
    const ex = D.byId(it.exId);
    const wLast = ex && ex.category === "strength" ? lastWeightOf(it.exId) : null;
    const wTxt = wNow ? `<span class="text-gold font-bold">💪 오늘 ${wNow}kg</span>`
      : wLast ? `<span class="text-zinc-500">지난 ${wLast.kg}kg</span>` : "";
    const dots = it.kind === "time"
      ? `<button class="w-11 h-11 rounded-xl border-2 font-extrabold ${done ? "bg-pri border-pri text-black" : "border-line text-zinc-500"}" data-i="0">✓</button>`
      : Array.from({ length: total }, (_, i) =>
        `<button class="w-11 h-11 rounded-xl border-2 font-extrabold text-[15px] transition ${i < done ? "bg-pri border-pri text-black" : "border-line text-zinc-500"}" data-i="${i}">${i + 1}</button>`).join("");
    const presc = it.kind === "time" ? esc(it.reps) : `${it.sets}세트 × ${esc(it.reps)}회`;
    return `<div class="rounded-2xl border ${full ? "border-pri/70 bg-pri/10" : "border-line bg-card2"} p-3.5 mb-2.5" data-ex="${it.exId}">
      <div class="flex items-start gap-2.5">
        <div class="flex-1 cursor-pointer" data-info="${it.exId}">
          <div class="font-bold text-[15px]"><span class="mr-1.5">${ex && ex.em ? ex.em : "🏋️"}</span>${esc(it.name)} <span class="text-zinc-500 text-[11px]">ⓘ</span></div>
          <div class="text-mut text-[12px] mt-1">
            <span class="text-pri2 font-bold">${esc(it.zone)}구역</span> · ${esc(it.equipment)} · ${presc}${it.rest ? ` · 휴식 ${it.rest}초` : ""}${wTxt ? " · " + wTxt : ""}</div>
          <div class="mt-1">${it.target.map((t) => `<span class="${CHIP} mr-1">${esc(t)}</span>`).join("")}</div></div>
        <button class="w-8 h-8 rounded-lg border border-line text-mut font-extrabold shrink-0" data-menu="${it.exId}">⋯</button></div>
      <div class="flex items-center gap-2 flex-wrap mt-3">${dots}
        <span class="ml-auto text-[12.5px] text-mut font-bold">${it.kind === "time" ? (done ? "완료" : "") : done + "/" + total + " 세트"}</span></div>
    </div>`;
  }

  function bindSets(pane, items) {
    $$("#exlist [data-ex]", pane).forEach((card) => {
      const exId = card.dataset.ex;
      const item = items.find((x) => x.exId === exId);
      $$("[data-i]", card).forEach((dot) => {
        dot.onclick = () => {
          const tw = todayWorkout() || { day: SEL_DAY, sets: {} };
          const cur = tw.sets[exId] || 0, i = +dot.dataset.i;
          if (item.kind === "time") tw.sets[exId] = cur > 0 ? 0 : 1;
          else tw.sets[exId] = (cur === i + 1) ? i : i + 1;
          S.saveWorkout(ME, S.today(), recompute(SEL_DAY, tw.sets, tw.items || items));
          const increased = tw.sets[exId] > cur;
          reload(); viewToday(pane);
          // 세트 완료 → 휴식 타이머 (마지막 세트 전까지)
          if (increased && item.rest && item.kind !== "time" && tw.sets[exId] < item.sets)
            startRest(item.rest, item.name);
        };
      });
    });
  }

  function recompute(dayNo, setsMap, items) {
    const dayPlan = USER.routine.week.find((d) => d.day === dayNo) || USER.routine.week[0];
    const list = items || dayPlan.items;
    const weight = CORE.weightOf(USER.profile);
    const score = CORE.sessionScore(list, setsMap);
    const kcal = Math.round(CORE.sessionKcalDone(list, weight, setsMap));
    const doneSets = Object.values(setsMap).reduce((a, b) => a + b, 0);
    const out = { day: dayNo, sets: setsMap, planned: score.planned, doneSets, scorePct: score.pct, kcal, ts: Date.now() };
    const tw = todayWorkout();
    if (tw && tw.items) out.items = tw.items;   // 오늘 커스텀 유지
    if (items && (!tw || !tw.items) && items !== dayPlan.items) out.items = items;
    if (tw && tw.weights) out.weights = tw.weights;   // 중량 기록 유지
    return out;
  }

  // 이 운동의 가장 최근 중량 기록 (오늘 제외)
  function lastWeightOf(exId) {
    const w = USER.workouts || {};
    const dates = Object.keys(w).filter((d) => d !== S.today()).sort().reverse();
    for (const d of dates) {
      if (w[d].weights && w[d].weights[exId]) return { kg: w[d].weights[exId], date: d };
    }
    return null;
  }

  // ── 오늘 운동 편집: 오늘 기록에 items 스냅샷을 만들어 그 위에서 수정 ──
  function ensureTw() {
    const dayPlan = USER.routine.week.find((d) => d.day === SEL_DAY) || USER.routine.week[0];
    const tw = todayWorkout() || { day: SEL_DAY, sets: {} };
    if (!tw.items) tw.items = JSON.parse(JSON.stringify(dayPlan.items));
    return tw;
  }
  function saveTw(tw) {
    S.saveWorkout(ME, S.today(), Object.assign(recompute(SEL_DAY, tw.sets, tw.items),
      { items: tw.items }, tw.weights ? { weights: tw.weights } : {}));
    reload();
  }

  function openExMenu(pane, exId) {
    const tw = ensureTw();
    const it = tw.items.find((x) => x.exId === exId);
    if (!it) return;
    const alts = D.EXERCISES.filter((e) => e.category === "strength" && e.id !== exId
      && e.primary.some((m) => (D.byId(exId) || { primary: [] }).primary.includes(m))
      && !tw.items.some((x) => x.exId === e.id)).slice(0, 5);
    const draw = () => {
      openSheet(`
      <h3 class="text-lg font-extrabold mb-1">${esc(it.name)}</h3>
      <p class="text-mut text-[12px] mb-4">오늘만 바꿔요 — 원래 루틴은 그대로 둡니다.</p>
      <div class="flex items-center justify-between rounded-xl border border-line bg-card2 px-4 py-3 mb-2.5">
        <span class="font-bold text-[14px]">세트 수</span>
        <div class="flex items-center gap-3">
          <button id="m-sm" class="w-9 h-9 rounded-lg bg-card border border-line font-extrabold">−</button>
          <b class="w-6 text-center">${it.sets}</b>
          <button id="m-sp" class="w-9 h-9 rounded-lg bg-card border border-line font-extrabold">+</button></div></div>
      <div class="flex items-center justify-between rounded-xl border border-line bg-card2 px-4 py-3 mb-2.5">
        <span class="font-bold text-[14px]">횟수</span>
        <input id="m-reps" class="w-28 bg-card border border-line rounded-lg px-2 py-2 text-center text-[13.5px] outline-none focus:border-pri" value="${esc(it.reps)}" /></div>
      <div class="flex items-center justify-between rounded-xl border border-line bg-card2 px-4 py-3 mb-3">
        <span class="font-bold text-[14px]">오늘 중량 <span class="text-mut text-[11px] font-normal">(선택)</span></span>
        <div class="flex items-center gap-1.5">
          <input id="m-kg" type="number" step="2.5" inputmode="decimal" class="w-20 bg-card border border-line rounded-lg px-2 py-2 text-center text-[13.5px] outline-none focus:border-pri placeholder:text-zinc-600"
            value="${(tw.weights && tw.weights[exId]) || ""}" placeholder="${(lastWeightOf(exId) || {}).kg || "kg"}" />
          <span class="text-mut text-[12px]">kg</span></div></div>
      ${alts.length ? `<h4 class="font-extrabold text-[13.5px] mb-2">🔄 같은 부위 다른 운동으로 교체</h4>
      <div class="space-y-1.5 mb-3">${alts.map((e) => `
        <button class="w-full text-left rounded-xl border border-line bg-card2 px-3.5 py-3" data-swap="${e.id}">
          <span class="mr-1">${e.em || "🏋️"}</span><b class="text-[13.5px]">${esc(e.name)}</b>
          <span class="text-mut text-[11.5px] ml-1.5">${esc(e.equipment)}</span></button>`).join("")}</div>` : ""}
      <button id="m-del" class="${BTN} w-full text-red-400 mb-2">🗑 오늘 목록에서 삭제</button>
      <button id="m-done" class="${BTNP} w-full">완료 ✅</button>`);
      $("#m-sm").onclick = () => { it.sets = Math.max(1, it.sets - 1); draw(); };
      $("#m-sp").onclick = () => { it.sets = Math.min(10, it.sets + 1); draw(); };
      $("#m-reps").oninput = (e) => { it.reps = e.target.value; };
      $("#m-kg").oninput = (e) => {
        const v = parseFloat(e.target.value);
        tw.weights = tw.weights || {};
        if (v > 0) tw.weights[exId] = v; else delete tw.weights[exId];
      };
      $("#m-done").onclick = () => { saveTw(tw); closeSheet(); viewToday(pane); };
      $("#m-del").onclick = () => {
        tw.items = tw.items.filter((x) => x.exId !== exId); delete tw.sets[exId];
        saveTw(tw); closeSheet(); viewToday(pane); toast("오늘 목록에서 뺐어요");
      };
      $$("[data-swap]").forEach((b) => b.onclick = () => {
        const ne = D.byId(b.dataset.swap);
        const idx = tw.items.findIndex((x) => x.exId === exId);
        tw.items[idx] = { exId: ne.id, name: ne.name, zone: ne.zone, equipment: ne.equipment,
          target: ne.primary.map((m) => D.MUSCLE_KR[m]), kind: ne.kind, sets: it.sets, reps: it.reps, rest: it.rest };
        delete tw.sets[exId];
        saveTw(tw); closeSheet(); viewToday(pane); toast(ne.name + "(으)로 교체! 🔄");
      });
    };
    draw();
  }

  function openTodayPicker(pane) {
    const tw = ensureTw();
    const groups = Object.keys(D.MUSCLE_KR).map((m) => ({
      kr: D.MUSCLE_KR[m], list: D.EXERCISES.filter((e) => e.primary[0] === m && !tw.items.some((x) => x.exId === e.id)),
    })).filter((g) => g.list.length);
    openSheet(`<h3 class="text-lg font-extrabold mb-1">오늘 운동 추가</h3>
      <p class="text-mut text-[12px] mb-3">오늘 목록에만 추가돼요.</p>` +
      groups.map((g) => `<div class="mb-3"><div class="text-mut text-[12px] font-bold mb-1.5">${g.kr}</div>
        <div class="space-y-1.5">${g.list.map((e) => `
          <button class="w-full text-left rounded-xl border border-line bg-card2 px-3.5 py-3" data-tadd="${e.id}">
            <span class="mr-1">${e.em || "🏋️"}</span><b class="text-[14px]">${esc(e.name)}</b>
            <span class="text-mut text-[12px] ml-1.5">${esc(e.equipment)}</span></button>`).join("")}</div></div>`).join(""), true);
    $$("[data-tadd]").forEach((b) => b.onclick = () => {
      const ne = D.byId(b.dataset.tadd);
      const st = D.STYLE_BY_ID[(USER.profile && USER.profile.style) || "health"];
      tw.items.push({ exId: ne.id, name: ne.name, zone: ne.zone, equipment: ne.equipment,
        target: ne.primary.map((m) => D.MUSCLE_KR[m]), kind: ne.kind,
        sets: ne.kind === "time" && ne.category === "cardio" ? 1 : st.sets,
        reps: ne.category === "cardio" ? "15분" : ne.kind === "time" ? "45-60초" : st.reps, rest: st.rest });
      saveTw(tw); closeSheet(); viewToday(pane); toast(ne.name + " 추가! ➕");
    });
  }

  // ── 운동 상세(동작 애니메이션 + 자극 부위) ──
  function openExercise(exId) {
    const ex = D.byId(exId);
    if (!ex) return;
    const motion = window.ANIM ? ANIM.motionSVG(ex.pat) : null;
    const muscles = window.ANIM ? ANIM.muscleSVG(ex.primary, ex.secondary) : "";
    const einfo = D.EQUIP_INFO[ex.equipment] || {};
    // 최근 중량 기록 (최대 6개)
    const w = USER.workouts || {};
    const whist = Object.keys(w).sort().reverse()
      .filter((d) => w[d].weights && w[d].weights[exId])
      .slice(0, 6).map((d) => ({ date: d, kg: w[d].weights[exId] }));
    openSheet(`
      <div class="flex items-center gap-3 mb-3">
        <div class="w-12 h-12 rounded-2xl bg-card2 border border-line flex items-center justify-center text-2xl">${ex.em || "🏋️"}</div>
        <div><h3 class="text-lg font-extrabold">${esc(ex.name)}</h3>
          <div class="text-[12px] text-mut">${esc(ex.zone)}구역 · ${esc(ex.equipment)}</div></div></div>
      <div class="grid grid-cols-2 gap-3 mb-4">
        <div class="rounded-xl border border-line bg-card2 p-2">
          <div class="h-36">${motion || '<div class="h-full flex items-center justify-center text-4xl">' + (ex.em || "🏋️") + "</div>"}</div>
          <div class="text-[10.5px] text-zinc-500 text-center mt-1">동작</div></div>
        <div class="rounded-xl border border-line bg-card2 p-2">${muscles}</div></div>
      <div class="flex gap-3 text-[11.5px] text-mut mb-4">
        <span class="flex items-center gap-1"><i class="w-2.5 h-2.5 rounded-full bg-red-500 inline-block"></i>주로 자극</span>
        <span class="flex items-center gap-1"><i class="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block"></i>보조 자극</span>
        <span class="ml-auto">${ex.primary.map((m) => D.MUSCLE_KR[m]).join("·")}${ex.secondary.length ? " (+" + ex.secondary.map((m) => D.MUSCLE_KR[m]).join("·") + ")" : ""}</span></div>
      ${ex.how ? `<h4 class="font-extrabold text-[14px] mb-2">이렇게 하세요</h4>
      <ol class="space-y-2 mb-4">${ex.how.map((s, i) => `
        <li class="flex gap-2.5 text-[13.5px] leading-relaxed">
          <span class="w-5 h-5 rounded-full bg-pri text-black text-[11px] font-extrabold flex items-center justify-center shrink-0 mt-0.5">${i + 1}</span>
          <span>${esc(s)}</span></li>`).join("")}</ol>` : ""}
      ${einfo.tip ? `<div class="rounded-xl border border-gold/50 bg-amber-950/30 p-3 text-[13px] leading-relaxed">💡 ${esc(einfo.tip)}</div>` : ""}
      ${whist.length ? `<h4 class="font-extrabold mt-4 mb-2 text-[14px]">📈 내 중량 기록</h4>
      <div class="rounded-xl border border-line bg-card2 divide-y divide-line/60">${whist.map((h, i) => {
        const prev = whist[i + 1];
        const diff = prev ? Math.round((h.kg - prev.kg) * 10) / 10 : 0;
        return `<div class="flex justify-between px-3.5 py-2.5 text-[13.5px]"><span class="text-mut">${h.date}</span>
          <span><b>${h.kg}kg</b>${diff ? ` <span class="text-[11px] ${diff > 0 ? "text-pri2" : "text-red-400"}">${diff > 0 ? "▲" : "▼"}${Math.abs(diff)}</span>` : ""}</span></div>`;
      }).join("")}</div>` : ""}`);
  }

  // ── 휴식 타이머 ──
  let restIv = null;
  function startRest(sec, name) {
    stopRest();
    let left = sec;
    const el = document.createElement("div");
    el.id = "rest-timer";
    el.className = "fixed left-1/2 -translate-x-1/2 bottom-20 z-40 w-[92%] max-w-sm bg-card border border-pri/60 rounded-2xl px-4 py-3 shadow-2xl";
    document.body.appendChild(el);
    const draw = () => {
      el.innerHTML = `<div class="flex items-center gap-3">
        <span class="text-[20px]">⏱️</span>
        <div class="flex-1"><div class="text-[12px] text-mut">${esc(name)} · 휴식</div>
          <div class="h-1.5 bg-black/40 rounded-full overflow-hidden mt-1">
            <div class="h-full bg-pri" style="width:${(left / sec) * 100}%"></div></div></div>
        <b class="text-[18px] tabular-nums">${Math.floor(left / 60)}:${String(left % 60).padStart(2, "0")}</b>
        <button id="rest-skip" class="text-[12px] text-mut font-bold">건너뛰기</button></div>`;
      $("#rest-skip").onclick = stopRest;
    };
    draw();
    restIv = setInterval(() => {
      left--;
      if (left <= 0) {
        stopRest(); toast("휴식 끝! 다음 세트 💪");
        if (navigator.vibrate) navigator.vibrate([150, 80, 150]);
      } else draw();
    }, 1000);
  }
  function stopRest() {
    clearInterval(restIv); restIv = null;
    const el = document.getElementById("rest-timer");
    if (el) el.remove();
  }

  // ═══════════════ 달력 ═══════════════
  function viewCalendar(pane) {
    const y = CAL.getFullYear(), m = CAL.getMonth();
    const startDow = new Date(y, m, 1).getDay();
    const daysIn = new Date(y, m + 1, 0).getDate();
    const w = USER.workouts || {}, todayS = S.today();
    // 러닝 기록도 날짜별로
    const runsBy = {};
    (USER.runs || []).forEach((r) => { (runsBy[r.date] = runsBy[r.date] || []).push(r); });

    let monthDays = 0, sumPct = 0, runDays = 0, runKm = 0;
    for (let d = 1; d <= daysIn; d++) {
      const k = S.fmt(new Date(y, m, d));
      if (w[k] && (w[k].doneSets || 0) > 0) { monthDays++; sumPct += w[k].scorePct || 0; }
      if (runsBy[k]) { runDays++; runsBy[k].forEach((r) => runKm += r.km); }
    }
    const avg = monthDays ? Math.round(sumPct / monthDays) : 0;

    let cells = ["일", "월", "화", "수", "목", "금", "토"].map((x, i) =>
      `<div class="text-center text-[11px] py-1 ${i === 0 ? "text-red-400/80" : "text-mut"}">${x}</div>`).join("");
    for (let i = 0; i < startDow; i++) cells += `<div></div>`;
    for (let d = 1; d <= daysIn; d++) {
      const k = S.fmt(new Date(y, m, d));
      const wk = w[k];
      const has = wk && (wk.doneSets || 0) > 0;
      const hasRun = !!runsBy[k];
      const dayKm = hasRun ? Math.round(runsBy[k].reduce((s, r) => s + r.km, 0) * 10) / 10 : 0;
      const fullDone = has && wk.scorePct >= 100;
      cells += `<button class="rounded-lg border h-[54px] p-1 flex flex-col items-start gap-[3px] overflow-hidden
        ${fullDone ? "bg-pri/15 border-pri/70" : has ? "bg-amber-900/25 border-gold/60" : hasRun ? "bg-sky-900/25 border-sky-500/50" : "bg-card2 border-line"}
        ${k === todayS ? "ring-2 ring-gold" : ""}" data-date="${k}">
        <span class="text-[10px] leading-none ${has || hasRun ? "font-extrabold" : "text-zinc-500"}">${d}</span>
        ${has ? `<span class="text-[8.5px] leading-none font-bold ${fullDone ? "text-pri2" : "text-gold"}">🏋️${wk.scorePct}%</span>` : ""}
        ${hasRun ? `<span class="text-[8.5px] leading-none font-bold text-sky-400">🏃${dayKm}k</span>` : ""}</button>`;
    }

    pane.innerHTML = `
    <div class="${CARD}">
      <div class="flex items-center justify-between mb-4">
        <button class="${BTN} !py-2 !px-3.5" data-mv="-1">‹</button>
        <b class="text-[16px]">${y}년 ${m + 1}월</b>
        <button class="${BTN} !py-2 !px-3.5" data-mv="1">›</button></div>
      <div class="grid grid-cols-7 gap-1.5">${cells}</div>
      <div class="flex justify-between mt-4 text-[13px] text-mut">
        <span>헬스 <b class="text-zinc-100">${monthDays}일</b> · 러닝 <b class="text-zinc-100">${runDays}일 ${Math.round(runKm * 10) / 10}km</b></span>
        <span>평균 달성률 <b class="text-zinc-100">${avg}%</b></span></div>
      <div class="flex gap-3.5 mt-2.5 text-[11px] text-mut flex-wrap">
        <span class="flex items-center gap-1"><i class="w-2.5 h-2.5 rounded bg-pri/40 border border-pri/70 inline-block"></i>헬스 100%</span>
        <span class="flex items-center gap-1"><i class="w-2.5 h-2.5 rounded bg-amber-900/60 border border-gold/60 inline-block"></i>헬스 부분</span>
        <span class="flex items-center gap-1"><i class="w-2.5 h-2.5 rounded-full bg-sky-400 inline-block"></i>러닝</span></div>
    </div>
    <div id="cal-detail" class="mt-3"></div>`;

    $$("[data-mv]", pane).forEach((b) => b.onclick = () => { CAL.setMonth(CAL.getMonth() + (+b.dataset.mv)); CAL_SEL = null; viewCalendar(pane); });
    $$("[data-date]", pane).forEach((c) => c.onclick = () => { CAL_SEL = c.dataset.date; calDetail(); });
    if (CAL_SEL) calDetail();

    function calDetail() {
      const wk = (USER.workouts || {})[CAL_SEL];
      const dayRuns = runsBy[CAL_SEL] || [];
      const el = $("#cal-detail");
      if (!wk && !dayRuns.length) {
        el.innerHTML = `<div class="${CARD}"><b>${CAL_SEL}</b><p class="text-mut text-sm mt-1.5">이 날은 운동 기록이 없어요.</p></div>`;
        return;
      }
      let html = "";
      if (wk) {
        const dayPlan = USER.routine.week.find((d) => d.day === wk.day) || USER.routine.week[0];
        const dayItems = wk.items || dayPlan.items;   // 그날 커스텀했으면 그 목록으로
        html += `<div class="${CARD}">
          <div class="flex items-center justify-between"><b>🏋️ ${CAL_SEL} · ${esc(dayPlan.typeKr)}</b>
            <span class="bg-gold text-amber-950 font-extrabold rounded-lg px-2 py-0.5 text-[13px]">${wk.scorePct}%</span></div>
          <div class="mt-3 divide-y divide-line/60">${dayItems.map((it) =>
            `<div class="flex justify-between py-2 text-[14px]"><span>${esc(it.name)}</span>
             <span class="text-mut">${wk.sets[it.exId] || 0}/${it.sets} 세트</span></div>`).join("")}</div>
          <div class="flex items-center justify-between mt-3">
            <span class="text-mut text-[13px]">🔥 ${wk.kcal} kcal</span>
            <button id="del-wk" class="text-red-400 text-[12.5px] font-bold">기록 삭제</button></div></div>`;
      }
      if (dayRuns.length) {
        html += `<div class="${CARD} mt-3">
          <b class="text-sky-400">🏃 러닝</b>
          <div class="mt-2 divide-y divide-line/60">${dayRuns.map((r) =>
            `<div class="flex justify-between py-2 text-[14px]"><span>${r.km}km</span>
             <span class="text-mut">${window.RUN.paceStr(r.paceSec)}/km</span></div>`).join("")}</div></div>`;
      }
      el.innerHTML = html;
      const del = $("#del-wk");
      if (del) del.onclick = () => { S.deleteWorkout(ME, CAL_SEL); reload(); CAL_SEL = null; viewCalendar(pane); toast("삭제했어요"); };
    }
  }

  // ═══════════════ 루틴 (내 루틴 + 만들기 + 공유) ═══════════════
  // ═══════════════ 분석 (그래프 통계) ═══════════════
  let STATS_MODE = "gym"; // gym | run
  let BW_FILTER = "all";  // 최고 중량 부위 필터

  // 바 차트 (SVG) — data: [{l:라벨, v:값}]
  function barChart(data, color, unit) {
    if (!data.length || data.every((d) => !d.v)) return `<p class="text-mut text-[13px] py-6 text-center">아직 데이터가 없어요</p>`;
    const W = 340, H = 130, pad = 4, bw = Math.min(30, (W - pad * 2) / data.length - 4);
    const max = Math.max(...data.map((d) => d.v), 0.1);
    let s = `<svg viewBox="0 0 ${W} ${H}" class="w-full">`;
    data.forEach((d, i) => {
      const x = pad + i * ((W - pad * 2) / data.length) + ((W - pad * 2) / data.length - bw) / 2;
      const h = Math.max(2, (d.v / max) * (H - 42));
      const y = H - 24 - h;
      s += `<rect x="${x}" y="${y}" width="${bw}" height="${h}" rx="3" fill="${color}" opacity="${d.v === max ? 1 : 0.65}"/>`;
      if (d.v > 0) s += `<text x="${x + bw / 2}" y="${y - 4}" font-size="8.5" fill="#a1a1aa" text-anchor="middle">${d.v}</text>`;
      s += `<text x="${x + bw / 2}" y="${H - 10}" font-size="8" fill="#71717a" text-anchor="middle">${d.l}</text>`;
    });
    return s + `</svg>` + (unit ? `<div class="text-right text-[10.5px] text-zinc-500 -mt-1">${unit}</div>` : "");
  }

  // 페이스 추이 라인 차트 — data: [{l, sec}] (낮을수록 빠름 → 위쪽)
  function paceChart(data) {
    const pts = data.filter((d) => d.sec);
    if (pts.length < 2) return `<p class="text-mut text-[13px] py-6 text-center">페이스 기록이 2개 이상 쌓이면 그래프가 나와요</p>`;
    const W = 340, H = 120, padX = 14, padY = 18;
    const min = Math.min(...pts.map((d) => d.sec)), max = Math.max(...pts.map((d) => d.sec));
    const span = Math.max(20, max - min);
    const x = (i) => padX + i * ((W - padX * 2) / (pts.length - 1));
    const y = (sec) => padY + ((sec - min) / span) * (H - padY * 2); // 빠를수록(작을수록) 위
    let line = pts.map((d, i) => `${x(i)},${y(d.sec)}`).join(" ");
    let s = `<svg viewBox="0 0 ${W} ${H}" class="w-full">
      <polyline points="${line}" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-linejoin="round"/>`;
    pts.forEach((d, i) => {
      const best = d.sec === min;
      s += `<circle cx="${x(i)}" cy="${y(d.sec)}" r="${best ? 4 : 3}" fill="${best ? "#fbbf24" : "#38bdf8"}"/>`;
      s += `<text x="${x(i)}" y="${y(d.sec) - 7}" font-size="8" fill="${best ? "#fbbf24" : "#71717a"}" text-anchor="middle">${window.RUN.paceStr(d.sec)}</text>`;
    });
    return s + `</svg><div class="text-right text-[10.5px] text-zinc-500 -mt-1">⭐ 노란 점 = 최고 페이스 · 위로 갈수록 빠름</div>`;
  }

  // 최근 N일 라벨 (MM/DD)
  function lastDays(n) {
    const out = [];
    for (let i = n - 1; i >= 0; i--) {
      const d = new Date(); d.setDate(d.getDate() - i);
      out.push({ key: S.fmt(d), l: (d.getMonth() + 1) + "/" + d.getDate() });
    }
    return out;
  }
  // 최근 N주 버킷 (이번주 포함, 월요일 시작)
  function lastWeeks(n) {
    const now = new Date();
    const mon = new Date(now); mon.setDate(now.getDate() - ((now.getDay() + 6) % 7)); mon.setHours(0, 0, 0, 0);
    const out = [];
    for (let i = n - 1; i >= 0; i--) {
      const st = new Date(mon); st.setDate(mon.getDate() - i * 7);
      const en = new Date(st); en.setDate(st.getDate() + 7);
      out.push({ st, en, l: i === 0 ? "이번주" : i + "주전" });
    }
    return out;
  }

  function viewStats(pane) {
    const w = USER.workouts || {}, runs = USER.runs || [];
    let html = `
    <div class="grid grid-cols-2 gap-1.5 mb-3 bg-card border border-line rounded-xl p-1">
      <button class="rounded-lg py-2.5 text-[13.5px] font-bold ${STATS_MODE === "gym" ? "bg-pri text-black" : "text-mut"}" data-sm="gym">🏋️ 헬스</button>
      <button class="rounded-lg py-2.5 text-[13.5px] font-bold ${STATS_MODE === "run" ? "bg-sky-500 text-sky-950" : "text-mut"}" data-sm="run">🏃 러닝</button>
    </div>`;

    if (STATS_MODE === "gym") {
      html += big3CardHtml();

      // 운동별 최고 중량 (⋯메뉴 중량 기록 기반)
      const bw = {};
      Object.keys(w).sort().forEach((d) => {
        const ws = w[d].weights || {};
        Object.keys(ws).forEach((ex) => {
          const kg = ws[ex];
          const cur = bw[ex] || (bw[ex] = { best: 0, bestDate: "", last: 0 });
          if (kg > cur.best) { cur.best = kg; cur.bestDate = d; }
          cur.last = kg;   // 날짜 오름차순이라 마지막이 최근
        });
      });
      const bwAll = Object.keys(bw).map((ex) => Object.assign({ ex }, bw[ex]))
        .sort((a, b) => b.best - a.best);
      // 부위별 필터 칩 (기록 있는 부위만 표시)
      const bwGroups = [...new Set(bwAll.map((r) => {
        const ex = D.byId(r.ex); return ex ? ex.primary[0] : null;
      }).filter(Boolean))];
      if (BW_FILTER !== "all" && !bwGroups.includes(BW_FILTER)) BW_FILTER = "all";
      const bwList = BW_FILTER === "all" ? bwAll
        : bwAll.filter((r) => { const ex = D.byId(r.ex); return ex && ex.primary[0] === BW_FILTER; });
      html += `<div class="${CARD} mb-3"><h3 class="font-extrabold mb-2">🏋️ 운동별 최고 중량</h3>
        ${bwAll.length ? `
        <div class="flex gap-1.5 overflow-x-auto pb-2 mb-1">
          <button class="shrink-0 rounded-full px-3 py-1.5 text-[12px] font-bold border ${BW_FILTER === "all" ? "bg-pri text-black border-pri" : "border-white/15 bg-white/5 text-mut"}" data-bwf="all">전체 ${bwAll.length}</button>
          ${bwGroups.map((m) => `<button class="shrink-0 rounded-full px-3 py-1.5 text-[12px] font-bold border ${BW_FILTER === m ? "bg-pri text-black border-pri" : "border-white/15 bg-white/5 text-mut"}" data-bwf="${m}">${D.MUSCLE_KR[m]}</button>`).join("")}
        </div>
        <div class="divide-y divide-line/60">${bwList.map((r) => {
          const ex = D.byId(r.ex);
          const up = r.last >= r.best;
          return `<div class="flex items-center justify-between py-2.5">
            <span class="text-[13.5px]">${ex ? (ex.em || "") + " " + esc(ex.name) : r.ex}
              <span class="text-[10.5px] text-zinc-500 ml-1">${ex ? D.MUSCLE_KR[ex.primary[0]] : ""}</span></span>
            <span class="text-right"><b class="text-[15px] text-gold">${r.best}kg</b>
              <span class="text-[10px] text-zinc-500 ml-1">${r.bestDate.slice(5).replace("-", "/")}</span>
              <div class="text-[10.5px] ${up ? "text-pri2" : "text-mut"}">최근 ${r.last}kg${up ? " 🔥" : ""}</div></span></div>`;
        }).join("")}</div>`
        : `<p class="text-mut text-[12.5px] mt-1 leading-relaxed">오늘 탭에서 운동의 ⋯ 메뉴 → <b>오늘 중량</b>을 기록하면 여기에 운동별 최고 기록이 쌓여요.</p>`}</div>`;

      const days14 = lastDays(14);
      const kcalData = days14.map((d) => ({ l: d.l.slice(d.l.indexOf("/") + 1), v: w[d.key] ? Math.round(w[d.key].kcal || 0) : 0 }));
      const weeks = lastWeeks(8).map((wb) => {
        let cnt = 0;
        Object.keys(w).forEach((k) => { const d = new Date(k + "T00:00:00"); if (d >= wb.st && d < wb.en && (w[k].doneSets || 0) > 0) cnt++; });
        return { l: wb.l, v: cnt };
      });
      const st = S.stats(USER);
      const pcts = Object.keys(w).filter((k) => (w[k].doneSets || 0) > 0).map((k) => w[k].scorePct || 0);
      const avgPct = pcts.length ? Math.round(pcts.reduce((a, b) => a + b, 0) / pcts.length) : 0;
      html += `
      <div class="${CARD} mb-3"><h3 class="font-extrabold mb-2">🔥 일별 소모 칼로리 <span class="text-mut text-[11.5px] font-normal">최근 14일</span></h3>
        ${barChart(kcalData, "#ccff00", "kcal")}</div>
      <div class="${CARD} mb-3"><h3 class="font-extrabold mb-2">📅 주별 운동 횟수 <span class="text-mut text-[11.5px] font-normal">최근 8주</span></h3>
        ${barChart(weeks, "#f59e0b", "일")}</div>
      <div class="${CARD}"><h3 class="font-extrabold mb-3">요약</h3>
        <div class="grid grid-cols-3 gap-2">
        ${[["총 운동", st.sessions + "회"], ["총 세트", st.totalSets], ["누적 kcal", st.totalKcal.toLocaleString()],
           ["평균 달성률", avgPct + "%"], ["최고 연속", st.best + "일"], ["레벨", "Lv." + st.level]]
          .map(([l, v]) => `<div class="bg-card2 border border-line rounded-xl py-2.5 text-center">
            <div class="font-extrabold text-[14px]">${v}</div><div class="text-[10px] text-mut mt-0.5">${l}</div></div>`).join("")}
        </div></div>`;
    } else {
      const recent = runs.slice(-14);
      const kmData = recent.map((r) => ({ l: r.date.slice(5).replace("-", "/"), v: r.km }));
      const paceData = recent.map((r) => ({ l: r.date.slice(5), sec: r.paceSec }));
      const weeks = lastWeeks(8).map((wb) => {
        let km = 0;
        runs.forEach((r) => { const d = new Date(r.date + "T00:00:00"); if (d >= wb.st && d < wb.en) km += r.km; });
        return { l: wb.l, v: Math.round(km * 10) / 10 };
      });
      const rst = window.RUN.stats(runs);
      html += `
      <div class="${CARD} mb-3"><h3 class="font-extrabold mb-2">🏃 회당 거리 <span class="text-mut text-[11.5px] font-normal">최근 ${recent.length}회</span></h3>
        ${barChart(kmData, "#38bdf8", "km")}</div>
      <div class="${CARD} mb-3"><h3 class="font-extrabold mb-2">⚡ 페이스 추이 <span class="text-mut text-[11.5px] font-normal">분'초"/km</span></h3>
        ${paceChart(paceData)}</div>
      <div class="${CARD} mb-3"><h3 class="font-extrabold mb-2">📅 주별 거리 <span class="text-mut text-[11.5px] font-normal">최근 8주</span></h3>
        ${barChart(weeks, "#818cf8", "km")}</div>
      <div class="${CARD}"><h3 class="font-extrabold mb-3">요약</h3>
        <div class="grid grid-cols-3 gap-2">
        ${[["총 러닝", rst.count + "회"], ["누적", rst.totalKm + "km"], ["이번달", rst.monthKm + "km"],
           ["최장 거리", rst.longest + "km"], ["최고 페이스", window.RUN.paceStr(rst.bestPace)], ["이번주", rst.weekKm + "km"]]
          .map(([l, v]) => `<div class="bg-card2 border border-line rounded-xl py-2.5 text-center">
            <div class="font-extrabold text-[14px]">${v}</div><div class="text-[10px] text-mut mt-0.5">${l}</div></div>`).join("")}
        </div></div>`;
    }
    pane.innerHTML = html;
    $$("[data-sm]", pane).forEach((b) => b.onclick = () => { STATS_MODE = b.dataset.sm; viewStats(pane); });
    $$("[data-bwf]", pane).forEach((b) => b.onclick = () => { BW_FILTER = b.dataset.bwf; viewStats(pane); });
    const b3s = $("#b3-start"); if (b3s) b3s.onclick = () => openBig3("start", pane);
    const b3m = $("#b3-measure"); if (b3m) b3m.onclick = () => openBig3("measure", pane);
    const b3g = $("#b3-goal"); if (b3g) b3g.onclick = () => openBig3("goal", pane);
  }

  // ── 3대 챌린지 (선택 참여) ──
  function big3CardHtml() {
    const b3 = USER.big3;
    if (!b3 || !b3.logs || !b3.logs.length) {
      return `<div class="${CARD} mb-3 !border-gold/50">
        <h3 class="font-extrabold">🏆 3대 챌린지</h3>
        <p class="text-mut text-[12.5px] mt-1.5 leading-relaxed">스쿼트 + 벤치 + 데드리프트 합계로 목표에 도전!
          현재 무게를 기록하고, 일정 기간마다 다시 측정해서 성장을 확인해요. <b>원하는 사람만!</b></p>
        <div class="flex gap-1.5 mt-2.5 text-[11px] text-mut">
          <span class="${CHIP}">3대 300 = 헬린이 졸업</span><span class="${CHIP}">400 = 중수</span><span class="${CHIP}">500 = 헬창 인증</span></div>
        <button id="b3-start" class="${BTNP} w-full mt-3 !py-2.5">도전 시작 🏆</button></div>`;
    }
    const last = b3.logs[b3.logs.length - 1];
    const total = Math.round((last.s + last.b + last.d) * 10) / 10;
    const pct = Math.min(100, Math.round(total / b3.goal * 100));
    const hist = b3.logs.slice(-8).map((l) => ({ l: l.date.slice(5).replace("-", "/"), v: Math.round(l.s + l.b + l.d) }));
    const first = b3.logs[0];
    const grow = Math.round((total - (first.s + first.b + first.d)) * 10) / 10;
    return `<div class="${CARD} mb-3 !border-gold/50">
      <div class="flex items-center justify-between">
        <h3 class="font-extrabold">🏆 3대 ${b3.goal} 챌린지</h3>
        <button id="b3-goal" class="text-[12px] text-mut font-bold">🎯 목표 변경</button></div>
      <div class="flex items-end gap-2 mt-2.5">
        <b class="disp text-[46px] leading-[0.85] text-gold">${total}</b>
        <span class="text-mut text-[13px] pb-0.5">/ ${b3.goal}kg ${grow > 0 ? `<span class="text-pri2 font-bold">(+${grow} 성장!)</span>` : ""}</span></div>
      <div class="h-5 bg-black/40 rounded-full overflow-hidden relative mt-2">
        <div class="h-full rounded-full bg-gradient-to-r from-amber-500 to-amber-300 transition-all duration-700" style="width:${pct}%"></div>
        <span class="absolute inset-0 flex items-center justify-center text-[11px] font-extrabold ${pct > 45 ? "text-amber-950" : "text-zinc-300"}">${pct}%</span></div>
      <div class="grid grid-cols-3 gap-2 mt-3">
        ${[["스쿼트", last.s], ["벤치", last.b], ["데드", last.d]].map(([l, v]) =>
          `<div class="bg-card2 border border-line rounded-xl py-2.5 text-center">
            <div class="font-extrabold text-[15px]">${v}<span class="text-[10px] text-mut font-normal">kg</span></div>
            <div class="text-[10px] text-mut mt-0.5">${l}</div></div>`).join("")}</div>
      ${hist.length >= 2 ? `<div class="mt-3">${barChart(hist, "#f59e0b", "kg 합계")}</div>` : ""}
      <button id="b3-measure" class="${BTNP} w-full mt-3 !py-2.5">📏 오늘 측정 기록하기</button>
      <p class="text-mut text-[11px] mt-2">마지막 측정: ${last.date} · 4~8주마다 다시 재보는 걸 추천!</p></div>`;
  }

  function openBig3(mode, pane) {
    const b3 = USER.big3 || { goal: 300, logs: [] };
    const last = b3.logs[b3.logs.length - 1] || { s: "", b: "", d: "" };
    const goalPick = mode !== "measure";
    const sbd = mode !== "goal";
    openSheet(`
      <h3 class="text-lg font-extrabold mb-1">🏆 3대 챌린지 ${mode === "measure" ? "— 측정 기록" : ""}</h3>
      <p class="text-mut text-[12.5px] mb-4">${mode === "measure" ? "오늘 잰 무게(1RM 또는 최고 무게)를 적어주세요." : "목표 합계를 고르세요. 나중에 바꿀 수 있어요."}</p>
      ${goalPick ? `<div class="grid grid-cols-3 gap-2 mb-2">
        ${[200, 250, 300, 350, 400, 500].map((g) =>
          `<button class="rounded-xl border py-3 font-extrabold text-[15px] ${b3.goal === g ? "border-gold bg-amber-950/40 text-gold" : "border-line bg-card2"}" data-b3g="${g}">${g}</button>`).join("")}</div>
      <input id="b3-custom" type="number" inputmode="numeric" class="w-full bg-card2 border border-line rounded-xl px-4 py-3 text-center outline-none focus:border-pri placeholder:text-zinc-600 mb-4" placeholder="직접 입력 (kg)" />` : ""}
      ${sbd ? `<div class="space-y-2.5 mb-2">
        ${[["b3-s", "🏋️ 스쿼트", last.s], ["b3-b", "🛏️ 벤치프레스", last.b], ["b3-d", "⬆️ 데드리프트", last.d]].map(([id, l, v]) => `
        <div class="flex items-center gap-3 rounded-xl border border-line bg-card2 px-4 py-3">
          <span class="flex-1 font-bold text-[14px]">${l}</span>
          <input id="${id}" type="number" step="2.5" inputmode="decimal" class="w-24 bg-card border border-line rounded-lg px-2 py-2 text-center outline-none focus:border-pri" value="${v}" />
          <span class="text-mut text-[12px]">kg</span></div>`).join("")}</div>` : ""}
      <button id="b3-save" class="${BTNP} w-full mt-2">저장 ✅</button>`);
    let goal = b3.goal;
    $$("[data-b3g]").forEach((el) => el.onclick = () => {
      goal = +el.dataset.b3g;
      $$("[data-b3g]").forEach((x) => x.className = `rounded-xl border py-3 font-extrabold text-[15px] ${+x.dataset.b3g === goal ? "border-gold bg-amber-950/40 text-gold" : "border-line bg-card2"}`);
    });
    $("#b3-save").onclick = () => {
      const custom = goalPick ? parseFloat($("#b3-custom").value) : 0;
      if (custom > 0) goal = custom;
      const nb = { goal, logs: (USER.big3 && USER.big3.logs || []).slice() };
      if (sbd) {
        const s = parseFloat($("#b3-s").value) || 0, b = parseFloat($("#b3-b").value) || 0, d = parseFloat($("#b3-d").value) || 0;
        if (!s && !b && !d) return toast("무게를 하나라도 넣어주세요");
        nb.logs = nb.logs.filter((l) => l.date !== S.today());
        nb.logs.push({ date: S.today(), s, b, d });
      }
      S.update(ME, { big3: nb }); reload();
      closeSheet(); viewStats(pane);
      const t = nb.logs.length ? nb.logs[nb.logs.length - 1] : null;
      toast(t && (t.s + t.b + t.d) >= goal ? "🎉 목표 달성!! 3대 " + goal + " 클리어!" : "기록 완료! 🏆");
    };
  }

  let SERVER_SHARED = null; // 서버 공유 루틴 캐시
  function viewRoutine(pane) {
    const r = USER.routine;
    const customs = USER.customs || [];
    let shared;
    if (window.SUPA && SUPA.enabled) {
      shared = SERVER_SHARED || S.sharedList();
      if (!SERVER_SHARED) SUPA.fetchShared().then((rows) => {
        if (rows && TAB === "routine") { SERVER_SHARED = rows; viewRoutine(pane); }
      });
    } else {
      shared = S.sharedList();
    }

    pane.innerHTML = `
    <div class="${CARD} mb-3">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-extrabold">내 루틴</h2>
        <button id="redo" class="text-[12.5px] text-mut font-bold">🔄 다시 진단</button></div>
      <div class="rounded-xl border border-pri/50 bg-pri/10 p-3 mt-3 text-[13.5px] font-bold">${esc(r.summary)}</div>
      <button id="show-schedule" class="${BTN} w-full !py-2.5 mt-2.5 text-[13.5px]">📆 전체 일정 한눈에 보기</button>
      <div class="mt-3 space-y-2">${r.week.map((d, di) => `
        <details class="rounded-xl border border-line bg-card2 overflow-hidden">
          <summary class="px-3.5 py-3 font-bold text-[14px] cursor-pointer list-none flex items-center justify-between">
            <span>Day ${d.day} · ${esc(d.typeKr)}</span>
            <span class="flex items-center gap-2">
              <button class="text-[11.5px] text-pri2 font-bold" data-editday="${di}">✏️ 편집</button>
              <span class="text-mut text-[12px]">${d.items.length}종 ▾</span></span></summary>
          <div class="px-3.5 pb-3 divide-y divide-line/60">${d.items.map((it) =>
            `<div class="flex justify-between py-2 text-[13.5px]"><span>${esc(it.name)}</span>
             <span class="text-mut">${it.kind === "time" ? esc(it.reps) : it.sets + "×" + esc(it.reps)}</span></div>`).join("")}</div>
        </details>`).join("")}</div>
      <p class="text-mut text-[11.5px] mt-2.5">✏️ 편집으로 플랜 자체를 내 맘대로 바꿀 수 있어요.</p>
    </div>

    <div class="${CARD} mb-3">
      <h3 class="font-extrabold mb-1">📚 유명 프로그램으로 시작하기</h3>
      <p class="text-mut text-[12px] mb-2.5">전 세계에서 검증된 방식 그대로 — 기간·횟수·종목이 정해져 있어요.</p>
      ${window.PROGRAMS.LIST.map((pg) => `
        <div class="rounded-xl border border-line bg-card2 p-3.5 mt-2.5">
          <div class="flex items-start justify-between gap-2">
            <div><b class="text-[14.5px]">${pg.emoji} ${esc(pg.name)}</b>
              <div class="text-[11.5px] mt-1">
                <span class="${CHIP} mr-1">📆 ${pg.weeks}주</span><span class="${CHIP} mr-1">주 ${pg.daysPerWeek}회</span>
                <span class="${CHIP} mr-1">${esc(pg.level)}</span><span class="${CHIP}">${esc(pg.goal)}</span></div></div></div>
          <div class="text-mut text-[12.5px] mt-2 leading-relaxed">${esc(pg.easy)}</div>
          <div class="flex gap-2 mt-3">
            <button class="${BTN} !py-2 !text-[12.5px] flex-1" data-pg-view="${pg.id}">자세히</button>
            <button class="${BTNP} !py-2 !text-[12.5px] flex-1" data-pg-apply="${pg.id}">이걸로 시작 🚀</button></div>
        </div>`).join("")}
    </div>

    <div class="${CARD} mb-3">
      <div class="flex items-center justify-between mb-1">
        <h3 class="font-extrabold">🛠️ 나만의 루틴</h3>
        <button id="new-custom" class="${BTNP} !py-2 !px-3.5 !text-[13px]">+ 만들기</button></div>
      ${customs.length === 0 ? `<p class="text-mut text-[13px] mt-2">원하는 운동으로 직접 짜서 쓰거나, 동료들과 공유해 보세요.</p>` :
        customs.map((c) => `
        <div class="rounded-xl border border-line bg-card2 p-3.5 mt-2.5">
          <div class="flex justify-between items-center"><b class="text-[14.5px]">${esc(c.name)}</b>
            <span class="text-mut text-[12px]">주 ${c.days.length}일${c.weeks ? " · " + c.weeks + "주 플랜" : ""}</span></div>
          <div class="flex gap-2 mt-3">
            <button class="${BTNP} !py-2 !text-[12.5px] flex-1" data-apply-c="${c.cid}">내 루틴으로</button>
            <button class="${BTN} !py-2 !text-[12.5px] flex-1" data-share-c="${c.cid}">📤 공유</button>
            <button class="${BTN} !py-2 !text-[12.5px] !px-3 text-red-400" data-del-c="${c.cid}">🗑</button></div>
        </div>`).join("")}
    </div>

    <div class="${CARD}">
      <h3 class="font-extrabold mb-1">🔥 추천·공유 루틴</h3>
      <p class="text-mut text-[12px] mb-2">동료들이 올린 루틴이에요. (지금은 예시 — 서버 연동 시 실제 공유)</p>
      ${shared.map((s) => `
        <div class="rounded-xl border border-line bg-card2 p-3.5 mt-2.5">
          <div class="flex justify-between items-start">
            <div><b class="text-[14.5px]">${esc(s.name)}</b>
              <div class="text-mut text-[12px] mt-0.5">by ${esc(s.author)} ${s.demo ? '· <span class="text-[10px]">예시</span>' : ""} · ${s.days.length}일</div></div>
            <button class="text-[12.5px] font-bold text-mut" data-like="${s.sid}">❤️ ${s.likes}</button></div>
          <div class="flex gap-2 mt-3">
            <button class="${BTN} !py-2 !text-[12.5px] flex-1" data-preview="${s.sid}">미리보기</button>
            <button class="${BTNP} !py-2 !text-[12.5px] flex-1" data-apply-s="${s.sid}">내 루틴으로</button></div>
        </div>`).join("")}
    </div>`;

    $("#redo").onclick = startOnboard;
    $("#show-schedule").onclick = openSchedule;
    $$("[data-editday]", pane).forEach((b) => b.onclick = (e) => { e.preventDefault(); e.stopPropagation(); openDayEditor(pane, +b.dataset.editday); });
    $$("[data-pg-view]", pane).forEach((b) => b.onclick = () => openProgram(b.dataset.pgView));
    $$("[data-pg-apply]", pane).forEach((b) => b.onclick = () => applyProgram(b.dataset.pgApply));
    $("#new-custom").onclick = () => openBuilder(null);
    $$("[data-apply-c]", pane).forEach((b) => b.onclick = () => {
      const c = customs.find((x) => x.cid === b.dataset.applyC);
      applyDays(c.days, c.name, c.weeks);
    });
    $$("[data-apply-s]", pane).forEach((b) => b.onclick = () => {
      const s = shared.find((x) => x.sid === b.dataset.applyS);
      applyDays(s.days, s.name, s.weeks);
    });
    $$("[data-share-c]", pane).forEach((b) => b.onclick = () => {
      const c = customs.find((x) => x.cid === b.dataset.shareC);
      S.shareRoutine(c, USER.id);
      if (window.SUPA && SUPA.enabled) {
        SUPA.insertShared({ sid: "s" + Date.now(), name: c.name, author: USER.id, days: c.days, likes: 0 });
        SERVER_SHARED = null; // 다음에 새로 불러오기
      }
      viewRoutine(pane); toast("공유했어요! 📤");
    });
    $$("[data-del-c]", pane).forEach((b) => b.onclick = () => { S.deleteCustom(ME, b.dataset.delC); reload(); viewRoutine(pane); });
    $$("[data-like]", pane).forEach((b) => b.onclick = () => {
      const sid = b.dataset.like;
      S.likeShared(sid);
      if (window.SUPA && SUPA.enabled && SERVER_SHARED) {
        const row = SERVER_SHARED.find((x) => x.sid === sid);
        if (row) { row.likes = (row.likes || 0) + 1; SUPA.likeShared(sid, row.likes); }
      }
      viewRoutine(pane);
    });
    $$("[data-preview]", pane).forEach((b) => b.onclick = () => {
      const s = shared.find((x) => x.sid === b.dataset.preview);
      openSheet(`<h3 class="text-lg font-extrabold mb-1">${esc(s.name)}</h3>
        <div class="text-mut text-[12.5px] mb-3">by ${esc(s.author)}</div>` +
        s.days.map((d, i) => `<div class="rounded-xl border border-line bg-card2 p-3.5 mb-2.5">
          <b class="text-[14px]">Day ${i + 1} · ${esc(d.name)}</b>
          <div class="divide-y divide-line/60 mt-1">${d.items.map((it) => {
            const ex = D.byId(it.exId);
            return `<div class="flex justify-between py-2 text-[13.5px]"><span>${ex ? esc(ex.name) : it.exId}</span>
              <span class="text-mut">${it.sets}×${esc(it.reps)}</span></div>`;
          }).join("")}</div></div>`).join("") +
        `<button class="${BTNP} w-full mt-2" id="sheet-apply">이 루틴을 내 루틴으로 💪</button>`);
      $("#sheet-apply").onclick = () => { closeSheet(); applyDays(s.days, s.name, s.weeks); };
    });

    function applyDays(days, name, weeks) {
      const routine = daysToRoutine(days, name, weeks);
      S.update(ME, { routine }); reload();
      toast("루틴을 적용했어요!"); TAB = "today"; renderMain();
    }
  }

  // ── 유명 프로그램 ──
  function openProgram(pgId) {
    const pg = window.PROGRAMS.byId(pgId);
    openSheet(`
      <h3 class="text-lg font-extrabold">${pg.emoji} ${esc(pg.name)}</h3>
      <div class="text-[11.5px] mt-1.5 mb-3">
        <span class="${CHIP} mr-1">📆 ${pg.weeks}주</span><span class="${CHIP} mr-1">주 ${pg.daysPerWeek}회</span>
        <span class="${CHIP} mr-1">${esc(pg.level)}</span><span class="${CHIP}">${esc(pg.goal)}</span></div>
      <p class="text-[13.5px] leading-relaxed">${esc(pg.desc)}</p>
      <div class="rounded-xl border border-gold/50 bg-amber-950/30 p-3 mt-3 text-[13px] leading-relaxed">💡 ${esc(pg.tip)}</div>
      ${pg.waves ? `<div class="rounded-xl border border-sky-500/40 bg-sky-950/30 p-3 mt-2 text-[12.5px]">
        🌊 4주 사이클: ${pg.waves.map((w) => `<b>${esc(w)}</b>`).join(" → ")}</div>` : ""}
      <h4 class="font-extrabold mt-4 mb-2 text-[14px]">구성</h4>
      ${pg.week.map((d, i) => `<div class="rounded-xl border border-line bg-card2 p-3.5 mb-2">
        <b class="text-[13.5px]">Day ${i + 1} · ${esc(d.name)}</b>
        <div class="divide-y divide-line/60 mt-1">${d.items.map((it) => {
          const ex = D.byId(it.exId);
          return `<div class="flex justify-between py-1.5 text-[13px]">
            <span>${ex ? (ex.em || "") + " " + esc(ex.name) : it.exId}</span>
            <span class="text-mut">${it.sets}×${esc(it.reps)}</span></div>`;
        }).join("")}</div></div>`).join("")}
      <button id="pg-go" class="${BTNP} w-full mt-2">이 프로그램으로 시작 🚀</button>`, true);
    $("#pg-go").onclick = () => { closeSheet(); applyProgram(pgId); };
  }
  function applyProgram(pgId) {
    const pg = window.PROGRAMS.byId(pgId);
    const routine = window.PROGRAMS.toRoutine(pg, S.today());
    S.update(ME, { routine }); reload();
    TAB = "today"; renderMain();
    toast(pg.name + " 시작! 🚀 " + pg.weeks + "주 화이팅!");
  }

  // ── 전체 일정 한눈에 (주차별 표) ──
  function openSchedule() {
    const r = USER.routine;
    const prog = programProgress(r);
    const totalWeeks = r.programWeeks || 8;
    const pg = r.programId ? window.PROGRAMS.byId(r.programId) : null;
    const curWeek = prog ? prog.week : 1;
    // 5/3/1처럼 주차마다 메인 횟수가 바뀌는 경우 반영
    const waveReps = ["5·5·5", "3·3·3", "5·3·1", "5×5 가볍게"];
    const repsFor = (it, w) => (r.programId === "five31" && it.reps === "5/3/1")
      ? waveReps[(w - 1) % 4] : esc(it.reps);

    let rows = "";
    for (let w = 1; w <= totalWeeks; w++) {
      const cur = w === curWeek;
      const wave = pg && pg.waves ? pg.waves[(w - 1) % pg.waves.length] : null;
      rows += `<details class="rounded-xl border mb-1.5 overflow-hidden
        ${cur ? "border-pri bg-pri/10" : w < curWeek ? "border-line bg-card2 opacity-60" : "border-line bg-card2"}" ${cur ? "open" : ""}>
        <summary class="flex items-center gap-2.5 px-3 py-2.5 cursor-pointer list-none">
          <span class="w-12 shrink-0 text-[12px] font-extrabold ${cur ? "text-pri2" : "text-mut"}">${w}주차</span>
          <div class="flex-1 flex flex-wrap gap-1">
            ${r.week.map((d) => `<span class="text-[10.5px] bg-black/30 border border-line rounded px-1.5 py-0.5">${esc(d.typeKr.split(" ")[0].split("(")[0])}</span>`).join("")}</div>
          ${wave ? `<span class="text-[10px] font-bold ${cur ? "text-sky-400" : "text-zinc-500"} shrink-0">${esc(wave)}</span>` : ""}
          ${w < curWeek ? `<span class="text-[11px] shrink-0">✔️</span>` : cur ? `<span class="text-[10px] font-extrabold text-pri2 shrink-0">지금</span>` : `<span class="text-[10px] text-zinc-600 shrink-0">▾</span>`}
        </summary>
        <div class="px-3 pb-3 border-t border-line/40">
          ${r.week.map((d) => `<div class="mt-2">
            <b class="text-[11.5px] ${cur ? "text-pri2" : "text-mut"}">Day ${d.day} · ${esc(d.typeKr)}</b>
            ${d.items.map((it) => `<div class="flex justify-between py-0.5 text-[12px]">
              <span class="text-zinc-300">${esc(it.name)}</span>
              <span class="text-mut">${it.kind === "time" ? esc(it.reps) : it.sets + "×" + repsFor(it, w)}</span></div>`).join("")}
          </div>`).join("")}
        </div>
      </details>`;
    }
    openSheet(`
      <h3 class="text-lg font-extrabold mb-1">📆 전체 일정</h3>
      <p class="text-mut text-[12.5px] mb-1.5">${esc(r.summary)}</p>
      ${prog ? `<div class="h-2 bg-black/40 rounded-full overflow-hidden mb-3.5">
        <div class="h-full bg-gradient-to-r from-pri to-pri2" style="width:${prog.pct}%"></div></div>` : `<div class="mb-3"></div>`}
      ${rows}
      <p class="text-mut text-[11.5px] mt-2 leading-relaxed">주차를 누르면 그 주에 뭘 하는지 펼쳐져요. 매주 같은 구성을 반복하고 Day는 운동한 순서대로 순환.${pg && pg.waves ? " 5/3/1은 주차마다 메인 리프트 횟수가 파도처럼 바뀌어요." : ""}</p>`, true);
  }

  // ── 내 루틴 Day 편집 (플랜 자체 수정) ──
  function openDayEditor(pane, di) {
    const r = USER.routine;
    const d = r.week[di];
    const draw = () => {
      openSheet(`
        <h3 class="text-lg font-extrabold mb-1">✏️ Day ${d.day} 편집</h3>
        <input id="de-name" class="w-full bg-card2 border border-line rounded-xl px-4 py-3 outline-none focus:border-pri my-3 text-[14px] font-bold" value="${esc(d.typeKr)}" />
        <div class="flex items-center gap-2 text-[10.5px] text-zinc-500 pb-1">
          <span class="flex-1">운동</span><span class="w-[100px] text-center">세트</span><span class="w-16 text-center">횟수</span><span class="w-6"></span></div>
        ${d.items.map((it, ii) => {
          const ex = D.byId(it.exId);
          return `<div class="flex items-center gap-2 py-2 border-b border-line/50">
            <span class="flex-1 text-[13.5px]">${ex ? (ex.em || "") + " " : ""}${esc(it.name)}</span>
            <button class="w-8 h-8 rounded-lg bg-card2 border border-line font-bold" data-dm="${ii}">−</button>
            <b class="w-5 text-center text-[13px]">${it.sets}</b>
            <button class="w-8 h-8 rounded-lg bg-card2 border border-line font-bold" data-dp="${ii}">+</button>
            <input class="w-16 bg-card2 border border-line rounded-lg px-1.5 py-1.5 text-center text-[12px]" data-dr="${ii}" value="${esc(it.reps)}" />
            <button class="text-red-400 text-[14px] px-1" data-dx="${ii}">✕</button></div>`;
        }).join("")}
        <button id="de-add" class="${BTN} w-full !py-2.5 mt-3">➕ 운동 추가</button>
        <button id="de-save" class="${BTNP} w-full mt-2">저장 ✅</button>`, true);
      $("#de-name").oninput = (e) => { d.typeKr = e.target.value; };
      $$("[data-dm]").forEach((b) => b.onclick = () => { const it = d.items[+b.dataset.dm]; it.sets = Math.max(1, it.sets - 1); draw(); });
      $$("[data-dp]").forEach((b) => b.onclick = () => { const it = d.items[+b.dataset.dp]; it.sets = Math.min(10, it.sets + 1); draw(); });
      $$("[data-dr]").forEach((b) => b.oninput = () => { d.items[+b.dataset.dr].reps = b.value; });
      $$("[data-dx]").forEach((b) => b.onclick = () => { d.items.splice(+b.dataset.dx, 1); draw(); });
      $("#de-add").onclick = () => {
        const groups = Object.keys(D.MUSCLE_KR).map((m) => ({
          kr: D.MUSCLE_KR[m], list: D.EXERCISES.filter((e) => e.primary[0] === m && !d.items.some((x) => x.exId === e.id)),
        })).filter((g) => g.list.length);
        openSheet(`<h3 class="text-lg font-extrabold mb-3">운동 고르기</h3>` +
          groups.map((g) => `<div class="mb-3"><div class="text-mut text-[12px] font-bold mb-1.5">${g.kr}</div>
            <div class="space-y-1.5">${g.list.map((e) => `
              <button class="w-full text-left rounded-xl border border-line bg-card2 px-3.5 py-3" data-dpick="${e.id}">
                <span class="mr-1">${e.em || "🏋️"}</span><b class="text-[14px]">${esc(e.name)}</b>
                <span class="text-mut text-[12px] ml-1.5">${esc(e.equipment)}</span></button>`).join("")}</div></div>`).join(""), true);
        $$("[data-dpick]").forEach((b2) => b2.onclick = () => {
          const ne = D.byId(b2.dataset.dpick);
          const st = D.STYLE_BY_ID[(USER.profile && USER.profile.style) || "health"];
          d.items.push({ exId: ne.id, name: ne.name, zone: ne.zone, equipment: ne.equipment,
            target: ne.primary.map((m) => D.MUSCLE_KR[m]), kind: ne.kind,
            sets: ne.kind === "time" && ne.category === "cardio" ? 1 : st.sets,
            reps: ne.category === "cardio" ? "15분" : ne.kind === "time" ? "45-60초" : st.reps, rest: st.rest });
          draw();
        });
      };
      $("#de-save").onclick = () => {
        if (!d.items.length) return toast("운동이 하나는 있어야 해요");
        if (!r.summary.includes("(수정됨)") && r.split !== "program" && r.split !== "custom") r.summary += " (수정됨)";
        S.update(ME, { routine: r }); reload();
        closeSheet(); renderMain(); toast("Day " + d.day + " 저장! ✏️");
      };
    };
    draw();
  }

  // 커스텀 days → 앱 표준 루틴 변환 (weeks 지정 시 그 기간으로 새로 시작)
  function daysToRoutine(days, name, weeks) {
    const styleId = (USER.profile && USER.profile.style) || "health";
    const st = D.STYLE_BY_ID[styleId];
    const old = USER.routine || {};
    const pw = weeks != null ? weeks : (old.programWeeks || 0);
    return {
      style: styleId, styleName: st.name, level: USER.profile ? USER.profile.level : "beginner",
      days: days.length, split: "custom", splitName: "커스텀",
      programWeeks: pw, startDate: weeks != null ? S.today() : (old.startDate || S.today()),
      summary: name + " · 주 " + days.length + "회" + (pw ? " · " + pw + "주" : ""),
      week: days.map((d, i) => ({
        day: i + 1, type: "custom", typeKr: d.name,
        items: d.items.map((it) => {
          const ex = D.byId(it.exId) || {};
          return { exId: it.exId, name: ex.name || it.exId, zone: ex.zone || "?", equipment: ex.equipment || "",
            target: (ex.primary || []).map((m) => D.MUSCLE_KR[m]), kind: ex.kind || "reps",
            sets: ex.kind === "time" && String(it.reps).includes("분") ? 1 : it.sets,
            reps: it.reps, rest: st.rest };
        }),
      })),
    };
  }

  // ── 루틴 빌더 ──
  function openBuilder(existing) {
    BUILDER = existing ? JSON.parse(JSON.stringify(existing))
      : { cid: "c" + Date.now(), name: "", weeks: 12, days: [{ name: "Day 1", items: [] }] };
    if (BUILDER.weeks == null) BUILDER.weeks = 12;
    drawBuilder();
  }
  function drawBuilder() {
    const b = BUILDER;
    openSheet(`
      <h3 class="text-lg font-extrabold mb-1">🛠️ 나만의 루틴 만들기</h3>
      <p class="text-mut text-[12px] leading-relaxed mb-3">💡 <b>일주일 구성만 짜면 매주 자동 반복</b>돼요 — 90일을 다 입력할 필요 없어요! 아래에서 몇 주 동안 돌릴지만 정하세요.</p>
      <input id="cb-name" class="w-full bg-card2 border border-line rounded-xl px-4 py-3 outline-none focus:border-pri mb-3" placeholder="루틴 이름 (예: 3달 벌크업 대작전)" value="${esc(b.name)}" />
      <div class="flex items-center gap-2 mb-3">
        <span class="text-mut text-[12.5px] font-bold shrink-0">기간</span>
        ${[[4, "4주"], [8, "8주"], [12, "12주(3달)"], [0, "계속"]].map(([v, t]) =>
          `<button class="flex-1 rounded-lg py-2 text-[12px] font-bold border ${b.weeks === v ? "bg-pri text-black border-pri" : "border-line bg-card2 text-mut"}" data-cbw="${v}">${t}</button>`).join("")}</div>
      <div id="cb-days">${b.days.map((d, di) => `
        <div class="rounded-xl border border-line bg-card2 p-3.5 mb-2.5">
          <div class="flex items-center gap-2 mb-2">
            <input class="flex-1 bg-transparent border-b border-line pb-1 text-[14px] font-bold outline-none" data-dname="${di}" value="${esc(d.name)}" />
            ${b.days.length > 1 ? `<button class="text-red-400 text-[12px] font-bold" data-ddel="${di}">삭제</button>` : ""}</div>
          ${d.items.length ? `<div class="flex items-center gap-2 text-[10px] text-zinc-500 pb-0.5">
            <span class="flex-1">운동</span><span class="w-[86px] text-center">세트</span><span class="w-14 text-center">횟수</span><span class="w-4"></span></div>` : ""}
          ${d.items.map((it, ii) => {
            const ex = D.byId(it.exId);
            return `<div class="flex items-center gap-2 py-1.5 border-b border-line/50 last:border-0">
              <span class="flex-1 text-[13.5px]">${ex ? esc(ex.name) : it.exId}</span>
              <button class="w-7 h-7 rounded-lg bg-card border border-line font-bold" data-sm="${di}:${ii}">−</button>
              <span class="w-5 text-center text-[13px] font-bold">${it.sets}</span>
              <button class="w-7 h-7 rounded-lg bg-card border border-line font-bold" data-sp="${di}:${ii}">+</button>
              <input class="w-14 bg-card border border-line rounded-lg px-1.5 py-1 text-center text-[12px]" data-reps="${di}:${ii}" value="${esc(it.reps)}" />
              <button class="text-red-400 text-[13px]" data-idel="${di}:${ii}">✕</button></div>`;
          }).join("")}
          <button class="${BTN} w-full !py-2 !text-[13px] mt-2" data-addex="${di}">+ 운동 추가</button>
        </div>`).join("")}</div>
      <button id="cb-addday" class="${BTN} w-full !py-2.5 mb-2">+ Day 추가</button>
      <button id="cb-save" class="${BTNP} w-full">저장하기 ✅</button>`, true);

    $("#cb-name").oninput = (e) => { b.name = e.target.value; };
    $$("[data-cbw]").forEach((el) => el.onclick = () => { b.weeks = +el.dataset.cbw; drawBuilder(); });
    $$("[data-dname]").forEach((el) => el.oninput = () => { b.days[+el.dataset.dname].name = el.value; });
    $$("[data-ddel]").forEach((el) => el.onclick = () => { b.days.splice(+el.dataset.ddel, 1); drawBuilder(); });
    $$("[data-idel]").forEach((el) => el.onclick = () => { const [di, ii] = el.dataset.idel.split(":"); b.days[+di].items.splice(+ii, 1); drawBuilder(); });
    $$("[data-sm]").forEach((el) => el.onclick = () => { const [di, ii] = el.dataset.sm.split(":"); const it = b.days[+di].items[+ii]; it.sets = Math.max(1, it.sets - 1); drawBuilder(); });
    $$("[data-sp]").forEach((el) => el.onclick = () => { const [di, ii] = el.dataset.sp.split(":"); const it = b.days[+di].items[+ii]; it.sets = Math.min(8, it.sets + 1); drawBuilder(); });
    $$("[data-reps]").forEach((el) => el.oninput = () => { const [di, ii] = el.dataset.reps.split(":"); b.days[+di].items[+ii].reps = el.value; });
    $$("[data-addex]").forEach((el) => el.onclick = () => openPicker(+el.dataset.addex));
    $("#cb-addday").onclick = () => { b.days.push({ name: "Day " + (b.days.length + 1), items: [] }); drawBuilder(); };
    $("#cb-save").onclick = () => {
      if (!b.name.trim()) return toast("루틴 이름을 넣어주세요");
      if (b.days.every((d) => d.items.length === 0)) return toast("운동을 하나 이상 추가해 주세요");
      S.saveCustom(ME, b); reload(); closeSheet();
      if (TAB === "routine") renderMain();
      toast("루틴을 저장했어요! 🛠️");
    };
  }
  // 운동 고르기(부위별)
  function openPicker(dayIdx) {
    const groups = Object.keys(D.MUSCLE_KR).map((m) => ({
      m, kr: D.MUSCLE_KR[m], list: D.EXERCISES.filter((e) => e.primary[0] === m),
    })).filter((g) => g.list.length);
    openSheet(`<h3 class="text-lg font-extrabold mb-3">운동 고르기</h3>` +
      groups.map((g) => `<div class="mb-3"><div class="text-mut text-[12px] font-bold mb-1.5">${g.kr}</div>
        <div class="space-y-1.5">${g.list.map((e) => `
          <button class="w-full text-left rounded-xl border border-line bg-card2 px-3.5 py-3 active:scale-[.99]" data-pick="${e.id}">
            <span class="font-bold text-[14px]">${esc(e.name)}</span>
            <span class="text-mut text-[12px] ml-1.5">${esc(e.equipment)}</span></button>`).join("")}</div></div>`).join(""), true);
    $$("[data-pick]").forEach((el) => el.onclick = () => {
      const ex = D.byId(el.dataset.pick);
      const styleId = (USER.profile && USER.profile.style) || "health";
      const defReps = ex.category === "cardio" ? "15분" : ex.kind === "time" ? "45초" : D.STYLE_BY_ID[styleId].reps;
      BUILDER.days[dayIdx].items.push({ exId: ex.id, sets: ex.kind === "time" && ex.category === "cardio" ? 1 : 3, reps: defReps });
      drawBuilder();
    });
  }

  // ═══════════════ 랭킹 ═══════════════
  const METRICS = [
    { id: "att", t: "출석률", unit: "%", get: (r) => r.att },
    { id: "streak", t: "연속출석", unit: "일", get: (r) => r.streak },
    { id: "sessions", t: "총 운동", unit: "회", get: (r) => r.sessions },
    { id: "xp", t: "XP", unit: "", get: (r) => r.xp },
  ];
  let SERVER_ROWS = null; // 서버 랭킹 캐시
  function viewRanking(pane) {
    const met = METRICS.find((x) => x.id === RANK_METRIC);
    let rows;
    if (window.SUPA && SUPA.enabled) {
      rows = (SERVER_ROWS || []).map((r) => ({ id: r.id, demo: false,
        att: r.stats.att || 0, streak: r.stats.streak || 0, sessions: r.stats.sessions || 0, xp: r.stats.xp || 0 }));
      if (!SERVER_ROWS) { // 최초 1회 서버에서 불러온 뒤 다시 그림
        SUPA.fetchStats().then((sr) => { if (sr && TAB === "ranking") { SERVER_ROWS = sr; viewRanking(pane); } });
        rows = S.ranking(); // 로딩 동안 로컬 표시
      }
    } else {
      rows = S.ranking();
    }
    rows.sort((a, b) => met.get(b) - met.get(a));
    const medals = ["🥇", "🥈", "🥉"];

    pane.innerHTML = `
    <div class="${CARD}">
      <h2 class="text-lg font-extrabold mb-3">🏆 사내 랭킹</h2>
      <div class="grid grid-cols-4 gap-1.5 mb-4 bg-card2 border border-line rounded-xl p-1">
        ${METRICS.map((m) => `<button class="rounded-lg py-2 text-[12.5px] font-bold ${RANK_METRIC === m.id ? "bg-pri text-black" : "text-mut"}" data-met="${m.id}">${m.t}</button>`).join("")}</div>
      <div class="space-y-2">${rows.map((r, i) => {
        const isMe = !r.demo && r.id.toLowerCase() === USER.id.toLowerCase();
        return `<div class="flex items-center gap-3 rounded-xl border px-3.5 py-3 ${isMe ? "border-pri bg-pri/10" : "border-line bg-card2"}">
          <span class="w-8 text-center text-[17px] font-extrabold">${medals[i] || (i + 1)}</span>
          <div class="flex-1"><b class="text-[14px]">${esc(r.id)}</b>
            ${isMe ? '<span class="ml-1.5 text-[10px] font-extrabold bg-pri text-black rounded px-1.5 py-0.5">나</span>' : ""}
            ${r.demo ? '<span class="ml-1.5 text-[10px] text-zinc-500">예시</span>' : ""}</div>
          <b class="text-[15px] ${isMe ? "text-pri2" : ""}">${met.get(r).toLocaleString()}<span class="text-[11px] text-mut font-normal">${met.unit}</span></b>
        </div>`;
      }).join("")}</div>
      <p class="text-mut text-[12px] leading-relaxed mt-4">${window.SUPA && SUPA.enabled
        ? "🟢 서버 연동됨 — 같은 앱을 쓰는 동료들과 실시간 랭킹이에요."
        : "'예시' 동료는 데모 데이터예요. 서버(Supabase)를 연동하면 실제 동료들과 경쟁할 수 있어요."} 출석률 = 최근 4주 계획 대비 실제 운동일.</p>
    </div>`;
    $$("[data-met]", pane).forEach((b) => b.onclick = () => { RANK_METRIC = b.dataset.met; viewRanking(pane); });
  }

  // ═══════════════ 헬스장 평면도 ═══════════════
  function viewGym(pane) {
    const zoneRects = D.FLOOR_ZONES.map((fz) => {
      const z = D.zoneById(fz.id);
      return `<g>
        <rect x="${fz.x}" y="${fz.y}" width="${fz.w}" height="${fz.h}" rx="10"
          fill="${z.color}0d" stroke="${z.color}55" stroke-width="1.2"/>
        <text x="${fz.x + 8}" y="${fz.y + 16}" font-size="9" font-weight="800" fill="${z.color}">${fz.id} · ${z.name}</text>
      </g>`;
    }).join("");
    const items = D.FLOOR.map((f) => {
      const z = D.zoneById(f.zone);
      return `<g class="cursor-pointer" data-eq="${esc(f.eq)}">
        <rect x="${f.x - 19}" y="${f.y - 15}" width="38" height="30" rx="7" fill="#18181b" stroke="${z.color}88" stroke-width="1"/>
        <text x="${f.x}" y="${f.y + 1}" font-size="12" text-anchor="middle">${f.icon}</text>
        <text x="${f.x}" y="${f.y + 11}" font-size="5.2" text-anchor="middle" fill="#a1a1aa">${esc(f.eq)}</text>
      </g>`;
    }).join("");

    pane.innerHTML = `
    <div class="${CARD}">
      <h2 class="text-lg font-extrabold">🗺️ 헬스장 평면도</h2>
      <p class="text-mut text-[12px] mt-0.5 mb-3">장비를 누르면 설명과 사용 팁이 나와요. (지금은 예시 배치)</p>
      <svg viewBox="0 0 400 310" class="w-full rounded-xl border border-line bg-black/30">
        ${zoneRects}${items}
        <g><rect x="178" y="300" width="44" height="8" rx="3" fill="#3f3f46"/>
        <text x="200" y="298" font-size="7" text-anchor="middle" fill="#a1a1aa">🚪 입구</text></g>
      </svg>
      <div class="flex flex-wrap gap-x-4 gap-y-1.5 mt-3">
        ${D.ZONES.map((z) => `<span class="flex items-center gap-1.5 text-[11.5px] text-mut">
          <i class="w-2.5 h-2.5 rounded-sm inline-block" style="background:${z.color}"></i>${z.id}구역 ${z.name}</span>`).join("")}
      </div>
    </div>
    <div class="${CARD} mt-3">
      <h3 class="font-extrabold mb-2">구역별 장비</h3>
      ${D.ZONES.map((z) => {
        const eqs = [...new Set(D.FLOOR.filter((f) => f.zone === z.id).map((f) => f.eq))];
        return `<div class="mb-2.5"><div class="text-[12.5px] font-bold" style="color:${z.color}">${z.id}구역 · ${z.name}</div>
          <div class="flex flex-wrap gap-1.5 mt-1.5">${eqs.map((e) =>
            `<button class="${CHIP} !py-1.5 !px-2.5 !text-[12px] active:scale-95" data-eq="${esc(e)}">${esc(e)}</button>`).join("")}</div></div>`;
      }).join("")}
    </div>`;

    $$("[data-eq]", pane).forEach((el) => el.onclick = () => openEquip(el.dataset.eq));
  }

  function openEquip(eq) {
    const info = D.EQUIP_INFO[eq] || {};
    const f = D.FLOOR.find((x) => x.eq === eq);
    const z = f ? D.zoneById(f.zone) : null;
    const uses = D.EXERCISES.filter((e) => e.equipment === eq);
    openSheet(`
      <div class="flex items-center gap-3.5 mb-3">
        <div class="w-14 h-14 rounded-2xl bg-card2 border border-line flex items-center justify-center text-3xl">${f ? f.icon : "🏋️"}</div>
        <div><h3 class="text-lg font-extrabold">${esc(eq)}</h3>
          ${z ? `<span class="text-[12px] font-bold" style="color:${z.color}">${z.id}구역 · ${z.name}</span>` : ""}</div></div>
      <p class="text-[14px] leading-relaxed">${esc(info.desc || "")}</p>
      ${info.tip ? `<div class="rounded-xl border border-gold/50 bg-amber-950/30 p-3 mt-3 text-[13px] leading-relaxed">💡 <b>팁</b> — ${esc(info.tip)}</div>` : ""}
      <h4 class="font-extrabold mt-4 mb-2 text-[14px]">이 장비로 하는 운동</h4>
      <div class="space-y-1.5">${uses.map((e) => `
        <div class="rounded-xl border border-line bg-card2 px-3.5 py-2.5 flex justify-between items-center">
          <span class="text-[13.5px] font-bold">${esc(e.name)}</span>
          <span class="text-[11.5px] text-mut">${e.primary.map((m) => D.MUSCLE_KR[m]).join("·")}</span></div>`).join("") || '<p class="text-mut text-[13px]">등록된 운동이 없어요.</p>'}</div>`);
  }

  // ═══════════════ 러닝 ═══════════════
  const R = window.RUN;
  let RUN_METRIC = "weekKm";

  function viewRun(pane) {
    if (!USER.runPlan) { // 선택 참여 — 시작 전 소개 화면
      pane.innerHTML = `
      <div class="${CARD} text-center py-10">
        <div class="text-[52px]">🏃</div>
        <h2 class="text-xl font-extrabold mt-3">러닝도 같이 할래요?</h2>
        <p class="text-mut text-[13.5px] mt-2 leading-relaxed px-4">몇 가지 질문으로 러닝 성향을 파악해서<br>
          <b class="text-zinc-200">이지런·템포·인터벌·장거리</b>를 섞은<br>주간 러닝 플랜을 짜드려요.</p>
        <p class="text-mut text-[12px] mt-3">하기 싫으면 안 해도 돼요 — 헬스 기능과는 별개!</p>
        <button id="run-start" class="${BTNP} mt-6 px-8 py-4 text-[16px]">러닝 시작하기 🏃</button>
      </div>
      <div class="${CARD} mt-3">
        <h3 class="font-extrabold mb-2 text-[14.5px]">러닝 훈련 타입이 뭔가요?</h3>
        ${Object.keys(R.TYPES).map((k) => { const t = R.TYPES[k];
          const hr = R.hrRange(k, (USER.profile && USER.profile.age) || 30);
          return `
          <div class="flex gap-3 py-2 border-b border-line/50 last:border-0">
            <span class="text-[20px]">${t.emoji}</span>
            <div><b class="text-[13.5px]" style="color:${t.color}">${t.kr}</b>
              <span class="text-mut text-[12px] ml-1">${t.easy}</span>
              <div class="text-mut text-[11.5px] mt-0.5 leading-relaxed">${t.guide}
                ${hr ? ` <span class="text-red-400/90 font-bold">💓 ${hr.lo}~${hr.hi}bpm</span>` : ""}</div></div></div>`; }).join("")}
      </div>`;
      $("#run-start").onclick = runOnboard;
      return;
    }

    const plan = USER.runPlan;
    const rp = USER.runProfile || {};
    const runs = USER.runs || [];
    const rst = R.stats(runs);
    const ws = R.weekScore(plan, runs);

    // 러닝 랭킹 데이터
    let rows;
    if (window.SUPA && SUPA.enabled && SERVER_ROWS) {
      rows = SERVER_ROWS.map((r) => ({ id: r.id, demo: false,
        weekKm: r.stats.weekKm || 0, monthKm: r.stats.monthKm || 0, totalKm: r.stats.totalKm || 0 }));
    } else {
      if (window.SUPA && SUPA.enabled && !SERVER_ROWS)
        SUPA.fetchStats().then((sr) => { if (sr && TAB === "run") { SERVER_ROWS = sr; viewRun(pane); } });
      rows = R.DEMO.concat([{ id: USER.id, demo: false, weekKm: rst.weekKm, monthKm: rst.monthKm, totalKm: rst.totalKm }]);
    }
    rows.sort((a, b) => (b[RUN_METRIC] || 0) - (a[RUN_METRIC] || 0));
    const medals = ["🥇", "🥈", "🥉"];
    const recent = runs.slice().reverse().slice(0, 7);

    pane.innerHTML = `
    <div class="${CARD} mb-3">
      <h2 class="text-lg font-extrabold mb-3">🏃 달린 기록</h2>
      <div class="mb-2.5"><label class="text-mut text-[12px] block mb-1">날짜 <span class="text-zinc-600">(과거 기록도 OK)</span></label>
        <input id="run-date" type="date" value="${S.today()}" max="${S.today()}"
          class="w-full bg-card2 border border-line rounded-xl px-3.5 py-2.5 outline-none focus:border-pri text-[14px] [color-scheme:dark]" /></div>
      <div class="flex gap-2.5">
        <div class="flex-1"><label class="text-mut text-[12px] block mb-1">거리 (km)</label>
          <input id="run-km" type="number" step="0.1" inputmode="decimal" placeholder="5.0"
            class="w-full bg-card2 border border-line rounded-xl px-3.5 py-3 outline-none focus:border-pri placeholder:text-zinc-600" /></div>
        <div class="flex-1"><label class="text-mut text-[12px] block mb-1">페이스 (분'초"/km)</label>
          <div class="flex items-center gap-1.5">
            <input id="run-pm" type="number" inputmode="numeric" placeholder="6"
              class="w-full bg-card2 border border-line rounded-xl px-3 py-3 text-center outline-none focus:border-pri placeholder:text-zinc-600" /><span class="text-mut">'</span>
            <input id="run-ps" type="number" inputmode="numeric" placeholder="30"
              class="w-full bg-card2 border border-line rounded-xl px-3 py-3 text-center outline-none focus:border-pri placeholder:text-zinc-600" /><span class="text-mut">"</span>
          </div></div></div>
      <button id="run-save" class="${BTNP} w-full mt-3">기록 저장 ✅</button>
    </div>

    <div class="${CARD} mb-3">
      <div class="lab mb-1">이번 주 거리 THIS WEEK</div>
      <div class="flex items-end gap-2">
        <span class="disp text-[64px] leading-[0.85] text-zinc-50">${ws.doneKm}</span>
        <span class="pb-1 text-mut font-bold text-[15px]">/ ${ws.targetKm} km</span>
        <b class="ml-auto pb-1 text-[19px] text-pri disp">${ws.pct}%</b></div>
      <div class="h-2.5 bg-white/10 rounded-full overflow-hidden relative mt-3">
        <div class="h-full rounded-full bg-pri transition-all duration-700" style="width:${ws.pct}%"></div></div>
      <div class="text-mut text-[12px] mt-2">${ws.pct >= 100 ? "이번 주 목표 달성! 🎉" : `목표까지 ${Math.max(0, Math.round((ws.targetKm - ws.doneKm) * 10) / 10)}km · ${ws.doneCnt}회 달림`}</div>
      <div class="grid grid-cols-4 gap-2 mt-4">
        ${[["이번주", rst.weekKm + "km"], ["이번달", rst.monthKm + "km"], ["누적", rst.totalKm + "km"], ["최고페이스", R.paceStr(rst.bestPace)]]
          .map(([l, v]) => `<div class="bg-white/[0.05] rounded-2xl py-2.5 text-center">
            <div class="disp text-[15px] leading-none">${v}</div><div class="text-[10px] text-mut mt-1">${l}</div></div>`).join("")}
      </div></div>

    <div class="${CARD} mb-3">
      <div class="flex items-center justify-between mb-1">
        <h3 class="font-extrabold">내 러닝 플랜</h3>
        <button id="run-redo" class="text-[12.5px] text-mut font-bold">🔄 다시 진단</button></div>
      <div class="rounded-xl border border-pri/50 bg-pri/10 p-3 text-[13px] font-bold mb-2.5">${esc(plan.summary)}</div>
      ${plan.week.map((d) => {
        const hr = R.hrRange(d.type, rp.age || (USER.profile && USER.profile.age) || 30, rp.maxHr);
        return `
        <div class="flex items-center gap-3 rounded-xl border border-line bg-card2 px-3.5 py-3 mb-2">
          <span class="text-[20px]">${d.emoji}</span>
          <div class="flex-1"><b class="text-[13.5px]" style="color:${d.color}">Day ${d.day} · ${esc(d.kr)}</b>
            <div class="text-mut text-[11.5px] mt-0.5 leading-relaxed">${esc(d.note)}</div>
            ${hr ? `<div class="text-[11.5px] mt-1"><span class="text-red-400 font-bold">💓 ${hr.lo}~${hr.hi}bpm</span>
              <span class="text-zinc-500">(최대심박의 ${hr.pctLo}~${hr.pctHi}%)</span></div>` : ""}</div>
          <b class="text-[15px]">${d.km}<span class="text-[11px] text-mut font-normal">km</span></b></div>`;
      }).join("")}
      <p class="text-mut text-[11.5px] leading-relaxed mt-1">💓 기준 최대심박 <b class="text-zinc-300">${rp.maxHr > 0 ? rp.maxHr + "bpm (직접 입력)" : (220 - (rp.age || 30)) + "bpm (220−나이)"}</b> × 훈련 강도%. 스마트워치가 있으면 이 범위 안에서 달려보세요.</p>
    </div>

    <div class="${CARD} mb-3">
      <h3 class="font-extrabold mb-3">🏆 러닝 랭킹</h3>
      <div class="grid grid-cols-3 gap-1.5 mb-3 bg-card2 border border-line rounded-xl p-1">
        ${[["weekKm", "이번주"], ["monthKm", "이번달"], ["totalKm", "누적"]].map(([k, t]) =>
          `<button class="rounded-lg py-2 text-[12.5px] font-bold ${RUN_METRIC === k ? "bg-pri text-black" : "text-mut"}" data-rmet="${k}">${t}</button>`).join("")}</div>
      <div class="space-y-2">${rows.map((r, i) => {
        const isMe = !r.demo && r.id.toLowerCase() === USER.id.toLowerCase();
        return `<div class="flex items-center gap-3 rounded-xl border px-3.5 py-2.5 ${isMe ? "border-pri bg-pri/10" : "border-line bg-card2"}">
          <span class="w-7 text-center text-[15px] font-extrabold">${medals[i] || (i + 1)}</span>
          <div class="flex-1"><b class="text-[13.5px]">${esc(r.id)}</b>
            ${isMe ? '<span class="ml-1.5 text-[10px] font-extrabold bg-pri text-black rounded px-1.5 py-0.5">나</span>' : ""}
            ${r.demo ? '<span class="ml-1.5 text-[10px] text-zinc-500">예시</span>' : ""}</div>
          <b class="text-[14px] ${isMe ? "text-pri2" : ""}">${(r[RUN_METRIC] || 0).toLocaleString()}<span class="text-[10.5px] text-mut font-normal">km</span></b></div>`;
      }).join("")}</div></div>

    <div class="${CARD}">
      <h3 class="font-extrabold mb-2">최근 기록</h3>
      ${recent.length === 0 ? `<p class="text-mut text-[13px]">아직 기록이 없어요. 오늘 첫 러닝을 저장해 보세요!</p>` :
        recent.map((r) => `<div class="flex items-center justify-between py-2.5 border-b border-line/50 last:border-0">
          <span class="text-[13.5px]">${esc(r.date)}</span>
          <span class="font-bold text-[14px]">${r.km}km</span>
          <span class="text-mut text-[13px]">${R.paceStr(r.paceSec)}/km</span>
          <button class="text-red-400 text-[12px]" data-rdel="${r.rid}">✕</button></div>`).join("")}
    </div>`;

    $("#run-save").onclick = () => {
      const km = parseFloat($("#run-km").value);
      if (!km || km <= 0) return toast("거리를 입력해 주세요");
      const date = $("#run-date").value || S.today();
      if (date > S.today()) return toast("미래 날짜는 안 돼요 😄");
      const pm = parseInt($("#run-pm").value) || 0, ps = parseInt($("#run-ps").value) || 0;
      const paceSec = pm * 60 + ps > 0 ? pm * 60 + ps : null;
      S.saveRun(ME, { date, km: Math.round(km * 100) / 100, paceSec });
      reload(); viewRun(pane);
      toast(date === S.today() ? `+${km}km 기록! 🏃` : `${date.slice(5)}에 ${km}km 기록! 🏃`);
    };
    $("#run-redo").onclick = runOnboard;
    $$("[data-rmet]", pane).forEach((b) => b.onclick = () => { RUN_METRIC = b.dataset.rmet; viewRun(pane); });
    $$("[data-rdel]", pane).forEach((b) => b.onclick = () => { S.deleteRun(ME, b.dataset.rdel); reload(); viewRun(pane); toast("삭제했어요"); });
  }

  // 러닝 성향 진단(시트)
  function runOnboard() {
    const RA = USER.runProfile ? Object.assign({}, USER.runProfile)
      : { exp: null, goal: null, days: 3, ability: null,
          age: (USER.profile && USER.profile.age) || 30, maxHr: 0 };
    if (!RA.age) RA.age = (USER.profile && USER.profile.age) || 30;
    draw();
    function draw() {
      const pickRow = (list, key, label) => `
        <h4 class="font-extrabold text-[14.5px] mt-5 mb-2">${label}</h4>
        <div class="grid grid-cols-2 gap-2">${list.map((o) => `
          <div class="rounded-xl border p-3 cursor-pointer ${RA[key] === o.v ? "border-pri bg-pri/10" : "border-line bg-card2"}" data-rq="${key}:${o.v}">
            <div class="font-bold text-[13.5px]">${o.t}</div>${o.d ? `<div class="text-mut text-[11.5px] mt-0.5">${o.d}</div>` : ""}</div>`).join("")}</div>`;
      openSheet(`
        <h3 class="text-lg font-extrabold">🏃 러닝 성향 진단</h3>
        <p class="text-mut text-[12.5px] mt-1">답에 맞춰 이지런·템포·인터벌·장거리를 섞은 주간 플랜을 만들어요.</p>
        ${pickRow(R.EXP, "exp", "러닝 경험은?")}
        ${pickRow(R.GOALS.map((g) => ({ v: g.id, t: g.emoji + " " + g.name, d: g.easy })), "goal", "목표는?")}
        ${pickRow([2, 3, 4, 5, 6].map((v) => ({ v, t: "주 " + v + "회" })), "days", "일주일에 몇 번 뛸까요?")}
        ${pickRow(R.ABILITY, "ability", "지금 쉬지 않고 달릴 수 있는 거리는?")}
        <h4 class="font-extrabold text-[14.5px] mt-5 mb-2">💓 목표 심박 계산용</h4>
        <div class="flex gap-2.5">
          <div class="flex-1"><label class="text-mut text-[12px] block mb-1">나이</label>
            <input id="rq-age" type="number" inputmode="numeric" value="${RA.age}"
              class="w-full bg-card2 border border-line rounded-xl px-3.5 py-3 text-center outline-none focus:border-pri" /></div>
          <div class="flex-1"><label class="text-mut text-[12px] block mb-1">최대심박 <span class="text-zinc-600">(아는 경우만)</span></label>
            <input id="rq-hr" type="number" inputmode="numeric" value="${RA.maxHr || ""}" placeholder="비우면 220−나이"
              class="w-full bg-card2 border border-line rounded-xl px-3.5 py-3 text-center outline-none focus:border-pri placeholder:text-zinc-600 placeholder:text-[11px]" /></div>
        </div>
        <p class="text-mut text-[11.5px] mt-2 leading-relaxed">스마트워치로 잰 최대심박이 있으면 넣어주세요 — 훈련별 목표 심박이 그 기준으로 맞춰져요.</p>
        <button id="run-make" class="${BTNP} w-full mt-5">러닝 플랜 만들기 ⚡</button>`, true);
      $("#rq-age").oninput = (e) => { RA.age = parseInt(e.target.value) || 30; };
      $("#rq-hr").oninput = (e) => { RA.maxHr = parseInt(e.target.value) || 0; };
      $$("[data-rq]").forEach((el) => el.onclick = () => {
        const [k, v] = el.dataset.rq.split(":");
        RA[k] = isNaN(+v) ? v : +v; draw();
      });
      $("#run-make").onclick = () => {
        if (!RA.exp) return toast("러닝 경험을 골라주세요");
        if (!RA.goal) return toast("목표를 골라주세요");
        if (!RA.ability) return toast("달릴 수 있는 거리를 골라주세요");
        const runPlan = R.buildPlan(RA);
        S.update(ME, { runProfile: RA, runPlan });
        reload(); closeSheet();
        TAB = "run"; renderMain();
        toast("러닝 플랜 완성! 🏃");
      };
    }
  }

  // ═══════════════ 내정보 시트 ═══════════════
  function openMe() {
    const p = USER.profile, r = USER.routine;
    const st = S.stats(USER);
    const cons = S.consistency28(USER, r.days);
    const fc = CORE.forecast(p, r, cons.ratio);
    const style = D.STYLE_BY_ID[r.style] || D.STYLE_BY_ID[p.style] || D.STYLES[5];
    const rows = [
      ["성별", p.sex === "female" ? "여성" : "남성"], ["나이", p.age + "세"],
      ["키 / 몸무게", p.height + "cm / " + (p.weight > 0 ? p.weight + "kg" : "미입력")],
      ["경력", D.LEVEL_KR[p.level] + (p.months >= 12 ? ` (${Math.round(p.months / 12)}년)` : ` (${p.months}개월)`)],
      ["목표 / 분할", style.name + " / " + r.splitName],
      ["주당 / 회당", p.days + "회 / " + p.sessionMin + "분"],
    ];
    openSheet(`
      <div class="flex items-center gap-3.5 mb-4">
        <div class="w-14 h-14 rounded-full bg-gradient-to-br from-amber-400 to-amber-600 text-amber-950 font-extrabold flex items-center justify-center text-[15px]">Lv${st.level}</div>
        <div><h3 class="text-lg font-extrabold">${esc(USER.id)}</h3>
          <div class="text-mut text-[12px]">${esc(USER.created)} 가입 · XP ${st.xp.toLocaleString()}</div></div></div>

      <div class="grid grid-cols-2 gap-2 mb-4">
        ${[["주간 소모(계획)", fc.weeklyKcal.toLocaleString() + " kcal"], ["예상 체지방 ↓", fc.monthlyFat + " kg/월"],
          ["예상 근육량 ↑", fc.monthlyMuscle + " kg/월"], ["4주 출석률", cons.pct + "% (" + cons.done + "/" + cons.planned + ")"]]
          .map(([l, v]) => `<div class="rounded-xl border border-line bg-card2 p-3">
            <div class="text-mut text-[11.5px]">${l}</div><div class="font-extrabold text-[16px] mt-0.5">${v}</div></div>`).join("")}
      </div>
      <div class="rounded-xl border border-pri/50 bg-pri/10 p-3 text-[13px] mb-4">🍽️ 식단 팁 — <b>${esc(style.name)}</b>: ${esc(style.surplus)}</div>

      <h4 class="font-extrabold text-[14px] mb-2">🏅 뱃지 (${st.badges.length}/${st.badgeDefs.length})</h4>
      <div class="grid grid-cols-3 gap-2 mb-4">${st.badgeDefs.map((b) => `
        <div class="rounded-xl border p-2.5 text-center ${st.badges.includes(b.id) ? "border-gold/70 bg-amber-950/20" : "border-line bg-card2 opacity-35"}">
          <div class="text-[12px] font-extrabold">${esc(b.name)}</div>
          <div class="text-[10px] text-mut mt-0.5">${esc(b.desc)}</div></div>`).join("")}</div>

      <div class="rounded-xl border border-line bg-card2 divide-y divide-line/60 mb-4">${rows.map(([k, v]) =>
        `<div class="flex justify-between px-3.5 py-2.5 text-[13.5px]"><span class="text-mut">${k}</span><b>${esc(v)}</b></div>`).join("")}</div>

      <button id="me-edit" class="${BTN} w-full mb-2">🔄 목표·루틴 다시 진단</button>
      <button id="me-settings" class="${BTN} w-full mb-2">⚙️ 개인정보·PIN 설정</button>
      <button id="me-logout" class="${BTN} w-full text-red-400">로그아웃</button>
      <p class="text-mut text-[11.5px] mt-3 leading-relaxed">예측치는 대략적 추정이며 식단·수면·개인차에 따라 달라집니다.</p>`, true);
    $("#me-edit").onclick = () => { closeSheet(); startOnboard(); };
    $("#me-settings").onclick = () => { closeSheet(); openSettings(); };
    $("#me-logout").onclick = () => { closeSheet(); S.logout(); ME = null; USER = null; renderLogin(); };
  }

  // ── 설정: 개인정보(성별·나이·키·몸무게) + PIN 변경 ──
  function openSettings() {
    const p = USER.profile || {};
    const fld = (id, label, val, unit, ph) => `
      <div class="mb-3"><label class="text-mut text-[13px] block mb-1.5">${label}</label>
        <div class="flex items-center gap-2">
          <input id="${id}" class="flex-1 bg-card2 border border-line rounded-xl px-4 py-3.5 outline-none focus:border-pri placeholder:text-zinc-600" type="number" inputmode="numeric" value="${val}" placeholder="${ph || ""}" />
          <span class="text-mut w-8">${unit}</span></div></div>`;
    openSheet(`
      <h3 class="text-lg font-extrabold mb-1">⚙️ 설정</h3>
      <p class="text-mut text-[12.5px] mb-4">개인정보는 여기서만 바꾸면 돼요 — 재진단 때는 안 물어봐요.</p>
      <div class="grid grid-cols-2 gap-2.5 mb-4">
        <div id="st-male" class="rounded-2xl border p-3.5 text-center font-bold cursor-pointer ${p.sex !== "female" ? "border-pri bg-pri/10" : "border-line bg-card2"}">🙋‍♂️ 남성</div>
        <div id="st-female" class="rounded-2xl border p-3.5 text-center font-bold cursor-pointer ${p.sex === "female" ? "border-pri bg-pri/10" : "border-line bg-card2"}">🙋‍♀️ 여성</div>
      </div>
      ${fld("st-age", "나이", p.age || 30, "세")}
      ${fld("st-height", "키", p.height || 172, "cm")}
      ${fld("st-weight", "몸무게 (선택)", p.weight > 0 ? p.weight : "", "kg", "비워도 돼요")}
      <div class="border-t border-line my-4"></div>
      <div class="mb-1"><label class="text-mut text-[13px] block mb-1.5">PIN 변경 (선택)</label>
        <input id="st-pin" type="password" inputmode="numeric" maxlength="4" class="w-full bg-card2 border border-line rounded-xl px-4 py-3.5 text-center tracking-[8px] outline-none focus:border-pri placeholder:text-zinc-600 placeholder:tracking-normal" placeholder="새 PIN 4자리 (바꿀 때만 입력)" /></div>
      <button id="st-save" class="${BTNP} w-full mt-4">저장 ✅</button>`, true);
    let sex = p.sex || "male";
    const paint = () => {
      $("#st-male").className = `rounded-2xl border p-3.5 text-center font-bold cursor-pointer ${sex !== "female" ? "border-pri bg-pri/10" : "border-line bg-card2"}`;
      $("#st-female").className = `rounded-2xl border p-3.5 text-center font-bold cursor-pointer ${sex === "female" ? "border-pri bg-pri/10" : "border-line bg-card2"}`;
    };
    $("#st-male").onclick = () => { sex = "male"; paint(); };
    $("#st-female").onclick = () => { sex = "female"; paint(); };
    $("#st-save").onclick = () => {
      const pin = $("#st-pin").value.trim();
      if (pin && !/^\d{4}$/.test(pin)) return toast("PIN은 숫자 4자리예요");
      const profile = Object.assign({}, USER.profile, {
        sex, age: parseFloat($("#st-age").value) || 30,
        height: parseFloat($("#st-height").value) || 172,
        weight: parseFloat($("#st-weight").value) || 0,
      });
      const upd = { profile };
      if (pin) upd.pin = pin;
      S.update(ME, upd);
      reload(); closeSheet(); renderMain();
      toast(pin ? "저장! PIN도 바꿨어요 🔐" : "저장했어요 ⚙️");
    };
  }

  // ═══════════════ 시작 ═══════════════
  (function init() {
    // 모바일↔데스크탑 전환 시 오늘 탭(대시보드) 다시 그리기
    if (window.matchMedia) {
      try { matchMedia("(min-width:1024px)").addEventListener("change", () => { if (USER && TAB === "today") renderMain(); }); } catch (e) {}
    }
    const cur = S.currentId();
    if (cur) {
      USER = S.getUser(cur);
      if (USER) {
        ME = USER.id;
        // 서버 연동 시 백그라운드로 최신 데이터 내려받기
        if (window.SUPA && SUPA.enabled) {
          SUPA.pullUser(ME).then((server) => {
            if (server && (server.profile || server.runProfile)) {
              S.replaceUser(ME, server); reload();
              if (TAB && $("#pane")) renderMain();
            }
          });
        }
        if (USER.profile && USER.routine) return renderMain();
        return startOnboard();
      }
    }
    renderLogin();
  })();
})();
