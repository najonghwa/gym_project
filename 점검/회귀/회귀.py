# -*- coding: utf-8 -*-
"""정제 탱크 시뮬레이터 회귀 시험 10종

계산을 바꾼 뒤 예전과 같은 결과가 나오는지 본다. 각 시험(t*.json)을 헤드리스 브라우저로 돌리고,
'OK/FAIL'과 마지막 결과 줄을 기준(기준_*.txt, 직전 배포판)과 나란히 적는다.

실행:  python 회귀.py [--only t78,tR] [--url 주소] [--high 고사양.html]
결과:  회귀결과.md, 회귀결과_<시험>.txt
- t78high(고사양 격자 계산)는 고사양 파일이 있어야 돌린다(--high).
"""
import argparse, json, pathlib, re, subprocess, sys, time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import 점검 as K   # 같은 실행 도구·브라우저·로컬 서버를 쓴다

TESTS = ["t107", "tD", "t78", "t95", "tR", "tP", "tP25", "tJ", "tH", "tV"]
WHAT = {"t107": "질량·열 수지(독립 계산과 비교)", "tD": "유출 = 받는 탱크 증가", "t78": "배치 끝까지(시각·초류·본류)", "t95": "스팀 개도 바꾸기",
        "tR": "레시피 단계 순서", "tP": "불러오기 0.5 s 뒤 점프", "tP25": "불러오기 2.5 s 뒤 점프", "tJ": "점프 뒤 흐름", "tH": "수동 조작 유지", "tV": "밸브 토글 때 점 수"}

def run_one(t, url):
    f = HERE / f"{t}.json"
    p = subprocess.run(["node", K.DRIVE, url, "--actions", str(f)], cwd=str(HERE), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=3600, env=K._browser_env())
    lines = [l for l in (p.stdout + p.stderr).splitlines() if not l.startswith("shot")]
    (HERE / f"회귀결과_{t}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    txt = "\n".join(lines)
    ev = [l for l in lines if l.startswith("eval")]
    return {"fail": len(re.findall(r"\b(FAIL|XX)\b", txt)), "ok": len(re.findall(r"\bOK\b", txt)), "clean": "console: clean" in txt, "last": ev[-1][6:] if ev else "", "code": p.returncode}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--only", default=""); ap.add_argument("--url", default=""); ap.add_argument("--high", default="")
    a = ap.parse_args()
    (HERE / "shots").mkdir(exist_ok=True)
    url = a.url or K.serve_local()
    only = [x for x in a.only.split(",") if x] or TESTS
    rows = ["# 회귀 시험 결과", "", f"{time.strftime('%Y-%m-%d %H:%M')} · {K.SIM_HTML.name}", "", "| 시험 | 내용 | 판정 | 이번 결과(마지막 줄) | 기준(직전 배포판) |", "|---|---|---|---|---|"]
    bad = 0
    for t in only:
        print("▶", t, flush=True)
        r = run_one(t, url + ("&" if "?" in url else "?") + "ex=1")
        base = (HERE / f"기준_{t}.txt").read_text(encoding="utf-8").strip() if (HERE / f"기준_{t}.txt").exists() else ""
        ok = r["fail"] == 0 and r["clean"] and r["code"] == 0
        bad += 0 if ok else 1
        rows.append(f"| {t} | {WHAT.get(t, '')} | {'통과' if ok else '**실패**'} (OK {r['ok']} · FAIL {r['fail']} · 콘솔 {'깨끗' if r['clean'] else '오류'}) | {r['last'][:260].replace('|', '/')} | {base[6:266].replace('|', '/')} |")
    if a.high:
        print("▶ t78high", flush=True)
        hp = pathlib.Path(a.high).resolve()
        r = run_one("t78", hp.as_uri() + "?ex=1")
        rows.append(f"| t78high | 고사양(격자) 배치 끝까지 | {'통과' if r['fail'] == 0 and r['clean'] else '**실패**'} | {r['last'][:260]} | |")
    (HERE / "회귀결과.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"실패 {bad} / {len(only)}  → 회귀결과.md")

if __name__ == "__main__":
    main()
