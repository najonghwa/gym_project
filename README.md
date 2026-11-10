# 정제 탱크 시뮬레이터

회분 정제(정제기 → 충전 컬럼 → 응축기 → 초류·본류 탱크)를 브라우저에서 돌려 보는 시뮬레이터.

현재 판: v86 · 11-10 14:36

## 받는 법

```bash
git clone -b distill-sim --single-branch https://github.com/najonghwa/gym_project.git distill-sim
```

새 판을 받을 때는 그 폴더에서 `git pull`.

git 없이 받으려면 아래 주소의 zip을 받는다.
https://github.com/najonghwa/gym_project/archive/refs/heads/distill-sim.zip

## 쓰는 법

1. 크롬이나 엣지로 `index.html`을 연다. 파일 하나로 동작하고 인터넷 없이 열린다.
2. 화면 제목 옆 판 번호가 위 '현재 판'과 같은지 확인한다.

## 그래픽이 약한 PC(VDI 등)

- 처음 몇 초 동안 속도를 재서, 그래픽 카드가 없으면 '가벼운 계산'(정제기 안 흐름 계산 끔)으로 자동 전환한다. 컬럼·응축기·배관 계산과 결과는 같다.
- 그래도 느리면 오른쪽 위 '도면으로 보기'를 누른다. 3D(WebGL)가 안 되는 PC에서는 도면 화면으로 시작한다.

## 운전 모드

- 레시피: 승온 → 전환류 안정화 → 초류 → 본류 순서로 자동 운전(유량·무게 입력 가능)
- 환류비 / 수동 / 자유: 운전 패널에서 고른다
