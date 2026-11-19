# -*- coding: utf-8 -*-
"""시뮬레이터에서 뽑은 기록(브라우저 실행 도구의 출력)을 값.json으로 정리한다.

실행:  python 값_모으기.py <실행 기록 파일>
- 기록은 레시피 운전을 0.5 · 2.5 · 6 · 30 · 58 h에 세우고 계산 값을 읽은 것이다(값_뽑기_동작.json이 그 동작 목록).
- 시점마다 PR(계산 상태) · CUR(입력) · fn(식 함수 값) · mix(액 물성)를 담는다.
"""
import io, json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
log = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
snaps = []; ver = None
for line in log.splitlines():
    if not line.startswith("eval: "): continue
    try: v = json.loads(line[6:])
    except Exception: continue
    if isinstance(v, str) and v.startswith("{"):
        try: o = json.loads(v)
        except Exception: continue
        if isinstance(o, dict) and "PR" in o and "CUR" in o: snaps.append(o)
want = ["0.5", "2.5", "6", "30", "58"]
assert len(snaps) == len(want), (len(snaps), "시점 수가 다르다")
out = {"snap": {}}
for k, s in zip(want, snaps):
    assert abs(s["PR"]["t_h"] - float(k)) < 0.2, (k, s["PR"]["t_h"])
    s.pop("cards", None); out["snap"][k] = s
(HERE / "값.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
p = out["snap"]["30"]["PR"]
print("값.json · 시점", ", ".join(f"{k} h" for k in want), "· 본류 30 h: 내부", p["Tmean"], "℃ · 정제기", p["Pstill"], "torr · 증발", p["vdot"], "kg/h")
