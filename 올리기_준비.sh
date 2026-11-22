#!/usr/bin/env bash
# 최신 정제 시뮬레이터(3D판, 파일 하나로 동작 — three.js·글꼴 내장)를 index.html 로 복사하고, 점검 도구(점검기·회귀 시험·실행 도구·작업 기준서)를 함께 맞춘다.
# 올리기: bash 올리기_준비.sh && git add -A && git commit -m "정제 시뮬레이터 vNN" && git push origin HEAD:distill-sim
# 개발 PC(외부망) 전용이다. 사내망에서는 index.html을 직접 고치므로 이 스크립트를 돌리지 않는다(돌리면 개발 PC 경로가 없어 멈춘다).
# 문서(적용_공식_정리.md·현장_데이터_맞춤_안내.md·사내망_합침_내역_v125.md·요구목록.md·요구현황.json)도 함께 올린다(2026-11-14 사용자 결정). 빼려면: WITH_DOCS=0 bash 올리기_준비.sh
set -e
cd "$(dirname "$0")"
cp "../정제탱크/정제_탱크_시뮬레이터.html" index.html
VER=$(grep -o 'v[0-9]* · [0-9-]* [0-9:]*' index.html | head -1)
if grep -q '<script[^>]*src="' index.html; then echo "경고: 외부 스크립트를 참조한다 — 파일 하나로 안 열린다"; exit 1; fi
sed -i "s/^현재 판: .*/현재 판: ${VER}/" README.md
K="../정제탱크/점검"
mkdir -p 점검/회귀 점검/도구
cp "$K/CLAUDE_저장소용.md" CLAUDE.md
cp "$K/점검.py" "$K/점검_공식.py" "$K/점검_합침.py" 점검/
cp "$K"/회귀/*.json "$K"/회귀/기준_*.txt "$K/회귀/회귀.py" "$K/회귀/회귀_표현.py" 점검/회귀/   # 회귀_표현.py: v132부터 기본 표현이 새 디자인이라 표현(lite · design)을 정해 돌린다
cp "$K"/도구/drive.mjs "$K"/도구/chrome-port.mjs "$K"/도구/line-ends.mjs "$K"/도구/LICENSE "$K"/도구/출처.md 점검/도구/
if [ "${WITH_DOCS:-1}" = "1" ]; then cp "../정제탱크/적용_공식_정리.md" "../정제탱크/현장_데이터_맞춤_안내.md" "../정제탱크/사내망_합침_내역_v125.md" .; cp "$K/요구목록.md" "$K/요구현황.json" 점검/; echo "문서 포함"; fi
# 발표자료 · 계산 흐름 학습(파일 하나로 열리는 HTML)과 만드는 소스(2026-11-19 사용자 요청). 소스는 발표자료/, 결과 HTML은 저장소 맨 위(index.html 옆)에 둔다.
# 다시 만들기: python 발표자료/만들기.py v130_최종 · python 발표자료/교과서.py v130_최종 · python 발표자료/흐름학습.py v130_최종(발표자료/점검결과_v130_최종.json을 읽는다).
# 시뮬레이터를 직접 돌리는 기록은 필요할 때만 다시 만든다: python 발표자료/시험계산.py 11.87 12.41 · python 발표자료/환류비_계산.py [--part fore](경우마다 5~15분). PIMS 화면 그림(png)은 저장소가 공개라 올리지 않는다.
if [ "${WITH_DECK:-1}" = "1" ]; then
  T="../정제탱크"; S="$T/발표자료"
  mkdir -p 발표자료
  cp "$T/정제_시뮬레이터_발표자료.html" "$T/정제_교과서.html" "$T/정제_계산_흐름_학습.html" .
  cp "$S"/*.py "$S/값.json" "$S/값_뽑기_동작.json" "$S/점검_겹침.js" "$S/요구목록_발표자료.md" "$S/점검결과_발표자료.md" "$S/요구목록_교과서.md" "$S/점검결과_교과서.md" "$S/코드_대조_결과.md" 발표자료/
  cp "$S/시험계산_기록.json" "$S/환류비_기록.json" "$S/환류비_기록_초류.json" "$S/DB값_양식.json" 발표자료/      # 시뮬레이터를 직접 돌린 기록(시험 계산 · 환류비별 계산)과 DB 값 표의 빈 양식
  # 현장 데이터는 공개 저장소에 올리지 않는다(2026-11-21 사용자): DB값.json · DB_맞춤_결과.json · 현장값_*.md는 .gitignore에 있다.
  # 이 폴더에서 문서를 다시 만들어 견줄 때만 쓰도록 DB값.json은 복사해 둔다(깃에는 안 들어간다. DB_맞춤_결과.json은 다시 만들 때 생긴다).
  cp "$S/DB값.json" 발표자료/
  cp "$S/시연_기록.json" "$S"/시연_화면_*.webp 발표자료/      # 발표 순서의 '시연 순서'가 읽는 기록과 화면 그림(시연_캡처.py가 시뮬레이터를 직접 눌러 남긴다. 시뮬레이터 판이 바뀌면 다시 돌린다)
  cp "$K/점검결과_v130_최종.json" 발표자료/      # 다시 만들 때 읽는 점검 기록(점검/점검결과*는 .gitignore라 발표자료/에 둔다)
  echo "발표자료 포함"
fi
echo "복사 완료: ${VER} ($(du -h index.html | cut -f1))"
