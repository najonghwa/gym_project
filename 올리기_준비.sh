#!/usr/bin/env bash
# 최신 정제 시뮬레이터(3D판, 파일 하나로 동작 — three.js·글꼴 내장)를 index.html 로 복사하고, 점검 도구(점검기·회귀 시험·실행 도구·작업 기준서)를 함께 맞춘다.
# 올리기: bash 올리기_준비.sh && git add -A && git commit -m "정제 시뮬레이터 vNN" && git push origin HEAD:distill-sim
# 문서(적용_공식_정리.md·요구목록.md·요구현황.json)는 공개 저장소라 기본으로 안 올린다. 올리려면: WITH_DOCS=1 bash 올리기_준비.sh
set -e
cd "$(dirname "$0")"
cp "../정제탱크/정제_탱크_시뮬레이터.html" index.html
VER=$(grep -o 'v[0-9]* · [0-9-]* [0-9:]*' index.html | head -1)
if grep -q '<script[^>]*src="' index.html; then echo "경고: 외부 스크립트를 참조한다 — 파일 하나로 안 열린다"; exit 1; fi
sed -i "s/^현재 판: .*/현재 판: ${VER}/" README.md
K="../정제탱크/점검"
mkdir -p 점검/회귀 점검/도구
cp "$K/CLAUDE_저장소용.md" CLAUDE.md
cp "$K/점검.py" 점검/
cp "$K"/회귀/*.json "$K"/회귀/기준_*.txt "$K/회귀/회귀.py" 점검/회귀/
cp "$K"/도구/drive.mjs "$K"/도구/chrome-port.mjs "$K"/도구/line-ends.mjs "$K"/도구/LICENSE "$K"/도구/출처.md 점검/도구/
if [ "${WITH_DOCS:-0}" = "1" ]; then cp "../정제탱크/적용_공식_정리.md" .; cp "$K/요구목록.md" "$K/요구현황.json" 점검/; echo "문서 포함"; fi
echo "복사 완료: ${VER} ($(du -h index.html | cut -f1))"
