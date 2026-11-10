#!/usr/bin/env bash
# 최신 정제 시뮬레이터(3D판, 인터넷 없이 동작하는 사내망 빌드)를 이 폴더로 복사한다.
#   index.html      ← 사내망_시뮬레이터_서버/distill_3d.html
#   lib/three.min.js ← 사내망_시뮬레이터_서버/lib/three.min.js
# 올리기: bash 올리기_준비.sh && git add -A && git commit -m "정제 시뮬레이터 vNN" && git push origin main:distill-sim
set -e
cd "$(dirname "$0")"
SRV="../사내망_시뮬레이터_서버"
mkdir -p lib
cp "$SRV/distill_3d.html" index.html
cp "$SRV/lib/three.min.js" lib/three.min.js
VER=$(grep -o 'v[0-9]* · [0-9-]* [0-9:]*' index.html | head -1)
if grep -q 'src="http' index.html; then echo "경고: 인터넷 주소의 스크립트를 참조한다 — 사내망에서 안 열린다"; exit 1; fi
sed -i "s/^현재 판: .*/현재 판: ${VER}/" README.md
echo "복사 완료: ${VER} ($(du -h index.html | cut -f1))"
