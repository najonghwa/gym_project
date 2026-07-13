// ── Supabase 연동 설정 ──
// 1) https://supabase.com 에서 무료 프로젝트 생성
// 2) 프로젝트 → SQL Editor 에서 supabase.sql 내용 실행 (테이블 생성)
// 3) 프로젝트 → Settings → API 에서 URL 과 anon public 키 복사해 아래에 붙여넣기
// 비워두면 서버 없이 동작합니다(기기 저장 + 예시 랭킹).
window.CONFIG = {
  SUPABASE_URL: "https://zfecjthzasudouskjusm.supabase.co",        // 예: "https://abcdefg.supabase.co"
  SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpmZWNqdGh6YXN1ZG91c2tqdXNtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM1MzQyMTQsImV4cCI6MjA5OTExMDIxNH0.gAKb-wZTRCkumCJOHUM4j0d1vJTXiDMqqrFjJEjalcI",   // 예: "eyJhbGciOi..."
};
