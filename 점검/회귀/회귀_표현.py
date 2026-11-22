# -*- coding: utf-8 -*-
"""회귀 시험 10종을 표현을 정해 돌린다(v132부터 기본 표현이 새 디자인이라 주소에 look=을 붙인다).
쓰기: python 회귀_표현.py lite|design [회귀.py 인자…]   결과: 회귀결과_<표현>.md (회귀결과.md를 복사)"""
import pathlib, shutil, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
LOOK = sys.argv[1]
assert LOOK in ("lite", "design"), LOOK
import 점검 as K  # noqa: E402

_orig = K.serve_local
K.serve_local = lambda *a, **k: _orig(*a, **k) + "?look=" + LOOK
import 회귀 as R  # noqa: E402

sys.argv = ["회귀.py"] + sys.argv[2:]
R.main()
shutil.copy(HERE / "회귀결과.md", HERE / f"회귀결과_{LOOK}.md")
print("복사:", f"회귀결과_{LOOK}.md")
