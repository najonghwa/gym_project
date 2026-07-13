-- 회사 헬스 가이드 — Supabase 테이블 생성 스크립트
-- Supabase 프로젝트 → SQL Editor → New query → 전체 붙여넣고 Run
--
-- 주의: 사내 데모용으로 누구나 읽기/쓰기 가능한 개방 정책입니다.
--       (비밀번호 없는 아이디 방식이라 의도된 설계 — 회사 외부 공개 시엔 Auth 도입 권장)

-- 사용자: 프로필·루틴·기록 전체를 jsonb 하나에, 랭킹용 요약은 stats에
create table if not exists public.gym_users (
  id text primary key,
  data jsonb not null default '{}'::jsonb,
  stats jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

-- 공유 루틴(업로드)
create table if not exists public.gym_shared_routines (
  sid text primary key,
  name text not null,
  author text not null,
  days jsonb not null,
  likes int not null default 0,
  ts date not null default current_date
);

-- RLS(행 수준 보안) 켜고, anon 키로 전부 허용
alter table public.gym_users enable row level security;
alter table public.gym_shared_routines enable row level security;

drop policy if exists "anon all gym_users" on public.gym_users;
create policy "anon all gym_users" on public.gym_users
  for all using (true) with check (true);

drop policy if exists "anon all gym_shared" on public.gym_shared_routines;
create policy "anon all gym_shared" on public.gym_shared_routines
  for all using (true) with check (true);
