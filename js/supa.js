// Supabase 연동 레이어 — config.js 에 URL/키가 있으면 활성화.
// 실패해도 앱이 멈추지 않게 전부 try/catch (오프라인/미설정 시 조용히 로컬만 사용).
window.SUPA = (function () {
  const C = window.CONFIG || {};
  let client = null;
  const enabled = !!(C.SUPABASE_URL && C.SUPABASE_ANON_KEY && window.supabase);
  if (enabled) {
    try { client = window.supabase.createClient(C.SUPABASE_URL, C.SUPABASE_ANON_KEY); }
    catch (e) { console.warn("supabase init fail", e); }
  }
  const ok = () => enabled && client;

  // 사용자 전체(data) + 랭킹 요약(stats) 업로드
  async function pushUser(user, stats) {
    if (!ok()) return;
    try {
      await client.from("gym_users").upsert({
        id: user.id.trim().toLowerCase(),
        data: user, stats: stats || {}, updated_at: new Date().toISOString(),
      });
    } catch (e) { console.warn("pushUser", e); }
  }
  // 사용자 내려받기(없으면 null)
  async function pullUser(id) {
    if (!ok()) return null;
    try {
      const { data } = await client.from("gym_users").select("data")
        .eq("id", id.trim().toLowerCase()).maybeSingle();
      return data ? data.data : null;
    } catch (e) { console.warn("pullUser", e); return null; }
  }
  // 랭킹용: 모든 사용자의 stats
  async function fetchStats() {
    if (!ok()) return null;
    try {
      const { data } = await client.from("gym_users").select("id, stats").limit(200);
      return data || [];
    } catch (e) { console.warn("fetchStats", e); return null; }
  }
  // 공유 루틴
  async function fetchShared() {
    if (!ok()) return null;
    try {
      const { data } = await client.from("gym_shared_routines")
        .select("*").order("ts", { ascending: false }).limit(50);
      return data || [];
    } catch (e) { console.warn("fetchShared", e); return null; }
  }
  async function insertShared(row) {
    if (!ok()) return;
    try { await client.from("gym_shared_routines").insert(row); }
    catch (e) { console.warn("insertShared", e); }
  }
  async function likeShared(sid, likes) {
    if (!ok()) return;
    try { await client.from("gym_shared_routines").update({ likes }).eq("sid", sid); }
    catch (e) { console.warn("likeShared", e); }
  }

  return { enabled: ok(), pushUser, pullUser, fetchStats, fetchShared, insertShared, likeShared };
})();
