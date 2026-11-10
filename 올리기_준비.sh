#!/usr/bin/env bash
# 최신 정제 시뮬레이터(3D판, 파일 하나로 동작 — three.js·글꼴 내장)를 index.html 로 복사한다.
# 올리기: bash 올리기_준비.sh && git add -A && git commit -m "정제 시뮬레이터 vNN" && git push origin main:distill-sim
set -e
cd "$(dirname "$0")"
cp "../정제탱크/정제_탱크_시뮬레이터.html" index.html
VER=$(grep -o 'v[0-9]* · [0-9-]* [0-9:]*' index.html | head -1)
if grep -q '<script[^>]*src="' index.html; then echo "경고: 외부 스크립트를 참조한다 — 파일 하나로 안 열린다"; exit 1; fi
sed -i "s/^현재 판: .*/현재 판: ${VER}/" README.md
echo "복사 완료: ${VER} ($(du -h index.html | cut -f1))"
