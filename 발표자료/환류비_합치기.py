# -*- coding: utf-8 -*-
"""환류비별 계산을 여러 창에서 나눠 돌린 기록을 합친다.

실행:  python 환류비_합치기.py [--fresh] 조각1.json 조각2.json ...
- 조각 = 환류비_계산.py에 --out을 줘서 따로 받은 기록. 구간(part)에 따라 환류비_기록.json(본류) · 환류비_기록_초류.json(초류)에 넣는다.
- 같은 경우(상대휘발도 · 환류 설정)가 이미 있으면 넣지 않는다. 판(ver) · 구간 · 환류 + 유출 합이 다르면 멈춘다.
- --fresh: 받는 쪽 기록을 비우고 조각만으로 다시 만든다(시뮬레이터 판이 바뀌어 전부 다시 돌렸을 때).
- 나눠 돌리는 예(세 창, 22경우 약 50분):
    python 환류비_계산.py --only 1.5 --out _workspace/rr_m15.json
    python 환류비_계산.py --only 20  --out _workspace/rr_m20.json
    python 환류비_계산.py --part fore --out _workspace/rr_f.json
    python 환류비_합치기.py --fresh _workspace/rr_m15.json _workspace/rr_m20.json _workspace/rr_f.json
"""
import io, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
DST = {"main": "환류비_기록.json", "fore": "환류비_기록_초류.json"}

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    fresh = "--fresh" in sys.argv; parts = [a for a in sys.argv[1:] if not a.startswith("--")]
    assert parts, "합칠 조각 파일을 적을 것"
    recs = {}
    for fn in parts:
        f = pathlib.Path(fn) if pathlib.Path(fn).is_absolute() else HERE / fn
        b = json.loads(f.read_text(encoding="utf-8")); assert b.get("runs"), f"{fn}: 기록이 없다"
        part = b["part"]; dst = HERE / DST[part]
        if part not in recs:
            recs[part] = dict(runs=[]) if (fresh or not dst.exists()) else json.loads(dst.read_text(encoding="utf-8"))
        a = recs[part]
        if a["runs"]:
            assert a["ver"] == b["ver"], f"{fn}: 판이 다르다({a['ver']} · {b['ver']}) — 전부 다시 돌렸으면 --fresh"
            assert a["vtot"] == b["vtot"] and a["part"] == b["part"], f"{fn}: 구간이나 환류 + 유출 합이 다르다"
        have = {(r["alpha"], r["R"]) for r in a["runs"]}; add = [r for r in b["runs"] if (r["alpha"], r["R"]) not in have]
        a["runs"] += add; a.update(ver=b["ver"], vtot=b["vtot"], part=part, note=b.get("note", a.get("note", "")), when=max(a.get("when", ""), b.get("when", "")))
        print(f"{fn}: {len(add)}건 넣음(이미 있던 것 {len(b['runs']) - len(add)}건)")
    for part, a in recs.items():
        a["runs"].sort(key=lambda r: (r["alpha"], r["R"]))
        assert len({r["ver"] for r in a["runs"]}) == 1, "기록마다 시뮬레이터 판이 다르다"
        by = {}
        for r in a["runs"]: by.setdefault(r["alpha"], []).append(r["R"])
        (HERE / DST[part]).write_text(json.dumps(a, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
        print(f"{DST[part]}: {len(a['runs'])}건 · {a['ver']} · " + " · ".join(f"상대휘발도 {k:g}: 환류 {v}" for k, v in sorted(by.items())))
