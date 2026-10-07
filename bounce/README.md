# Bounce

빨간 공을 굴려 링을 모두 모으고 출구로 들어가는 HTML5 웹게임입니다. 설치할 것 없이 `index.html` 하나로 동작해요.

- 플레이: https://enhkm.github.io/yolo26-webcam/bounce/
- 저장소: https://github.com/enhkm/yolo26-webcam (`bounce/` 폴더)

## 조작법
- ← → / A D: 이동
- Space / ↑ / W: 점프 (길게 누르면 더 높이 뛰어요)
- P / Esc: 일시정지
- 모바일: 화면 아래 터치 버튼

## 규칙
- 링을 모두 모으면 출구가 열려요
- 가시에 닿거나 구덩이에 빠지면 목숨이 하나 줄어요 (총 3개)
- 노란 스프링을 밟으면 높이 튀어 올라요
- 레벨은 총 3개예요

## 로컬 실행
`index.html` 파일을 브라우저로 열면 바로 플레이할 수 있어요.

---

# 강의노트: HTML 웹게임을 만들어 GitHub Pages로 배포하기

> 작업일: 2026-10-07
> 목표: HTML 파일 하나로 된 웹게임을 만들고, git으로 기록하고, GitHub에 올리고, GitHub Pages로 누구나 접속할 수 있게 배포한다.
>
> 참고: 처음에는 별도 저장소 `enhkm/bounce-game`에 올렸다가, 이후 `enhkm/yolo26-webcam` 저장소의 `bounce/` 폴더로 옮겼어요. 아래 4강의 저장소 생성 과정은 처음 올릴 때 기록이에요.

## 학습 목표
이 노트를 다 보고 나면 다음을 할 수 있어요.
1. 캔버스(`<canvas>`)로 간단한 2D 게임의 기본 구조를 이해한다.
2. 브라우저 화면을 직접 띄워 로컬에서 동작을 확인한다.
3. `git commit` → GitHub `push` → GitHub Pages 배포의 흐름을 설명할 수 있다.
4. 작업 중 만난 오류의 원인을 찾고 다른 방법으로 해결할 수 있다.

## 전체 흐름 한눈에 보기

```
[1] 게임 파일 작성 → [2] 로컬 실행 확인 → [3] git commit → [4] GitHub push → [5] Pages 배포 → [6] 접속 확인
```

| 단계 | 결과 |
|---|---|
| 1. 게임 파일 생성 | `index.html`, `README.md` 작성 |
| 2. 로컬 실행 확인 | Edge 헤드리스 모드로 화면 캡처, 키 입력으로 시작/이동/점프 확인 |
| 3. git commit | `ef58d5e Add Bounce HTML5 web game` |
| 4. GitHub push | `enhkm/bounce-game` 공개 저장소 생성 후 `main` 브랜치 push |
| 5. Pages 배포 | `main` 브랜치의 루트(`/`)를 Pages 소스로 지정 |
| 6. 접속 확인 | 빌드 상태 `built`, 사이트 응답 HTTP 200 |

---

## 1강. 게임 파일 만들기

### 왜 파일 하나로 만들었나?
GitHub Pages는 **정적 파일**(HTML, CSS, JS)만 그대로 보여주는 서비스예요. 서버 프로그램이나 빌드 과정이 필요 없도록 HTML, CSS, JavaScript를 `index.html` 하나에 모두 넣었어요. Pages는 폴더에 접속하면 자동으로 `index.html`을 열어주기 때문에 파일 이름도 중요해요.

### 게임의 기본 구조: 게임 루프
거의 모든 실시간 게임은 아래 구조를 1초에 약 60번 반복해요.

```js
function frame(now) {
  const dt = Math.min(0.05, (now - last) / 1000); // 지난 프레임 이후 흐른 시간(초)
  last = now;
  update(dt);   // 1) 위치, 속도, 충돌 등 상태 계산
  render();     // 2) 계산된 상태를 화면에 그리기
  requestAnimationFrame(frame); // 3) 다음 프레임 예약
}
```

- `dt`(delta time)를 곱해서 움직이면 컴퓨터 속도와 상관없이 같은 속도로 움직여요.
- `Math.min(0.05, ...)`로 상한을 둔 이유: 탭을 잠깐 내렸다 돌아오면 `dt`가 갑자기 커져서 공이 벽을 뚫고 지나갈 수 있기 때문이에요.

### 맵을 코드로 만들기
처음에는 맵을 문자열 그림으로 그리려 했지만, 칸 수를 하나만 잘못 세어도 플랫폼 위치가 어긋나요. 그래서 **함수로 맵을 짓는 방식**을 택했어요.

```js
b.ground(0, 14);        // 0~13칸에 바닥
b.plat(8, 6, 3);        // (8, 6)에서 3칸짜리 발판
b.ring(9, 5);           // (9, 5)에 링
b.spike(26, 8, 2);      // (26, 8)에서 가시 2개
b.exit(57, 7);          // 출구 위치
```

> 💡 포인트: 데이터를 사람이 손으로 정렬하는 형식보다, 의도(“여기에 3칸짜리 발판”)를 그대로 적는 형식이 실수가 적어요.

### 물리와 충돌
- 중력: 매 프레임 `vy += G * dt`
- 점프: 바닥에 있을 때 `vy = -JUMP`
- 충돌은 **X축과 Y축을 따로** 처리해요. 먼저 가로로 움직여서 벽과 부딪쳤는지 보고, 그다음 세로로 움직여서 바닥과 천장을 확인해요. 한꺼번에 처리하면 모서리에서 어느 방향으로 밀어내야 할지 헷갈려서 공이 끼거나 튀어요.
- 한 프레임을 1/120초 단위로 나눠서(서브스텝) 계산해 빠르게 떨어질 때 바닥을 뚫는 문제를 막았어요.

### 레벨이 깰 수 있는지 계산으로 확인하기
점프 높이와 거리를 미리 계산해서 발판과 구덩이 간격을 정했어요.

| 값 | 계산 | 결과 |
|---|---|---|
| 최대 점프 높이 | `JUMP² / (2 × G)` = 690² / 3600 | 약 132px (약 4칸) |
| 공중에 떠 있는 시간 | `2 × JUMP / G` = 1380 / 1800 | 약 0.77초 |
| 최대 점프 거리 | 0.77초 × 235px/s | 약 180px (약 5.6칸) |

그래서 구덩이는 4칸 이하, 발판 높이 차이는 3칸 이하로 만들었어요.

---

## 2강. 로컬에서 실행 확인하기

코드를 다 썼다고 끝이 아니에요. **실제로 브라우저에서 돌아가는지** 봐야 해요.

1. Edge를 헤드리스 모드(창 없이 실행)로 띄워 화면을 캡처했어요.
   ```powershell
   msedge.exe --headless=new --window-size=1000,500 --virtual-time-budget=1500 --screenshot=shot.png file:///.../index.html
   ```
2. 테스트용 사본에 키 입력을 흉내 내는 스크립트를 넣어서 Space로 시작하고 → 키로 이동하고 점프하는 것을 확인했어요.
   ```js
   dispatchEvent(new KeyboardEvent('keydown', { code: 'Space' }));
   ```

> ⚠️ 한계: 자동 테스트로는 시작, 이동, 점프까지만 봤어요. 3개 레벨을 처음부터 끝까지 직접 깨 보는 것은 아직 사람이 해야 해요.

---

## 3강. git commit

```powershell
git add index.html README.md
git commit -m "Add Bounce HTML5 web game"
git branch -M main
```

- `git add`: 이번 기록에 넣을 파일을 고르기
- `git commit`: 고른 파일의 현재 모습을 하나의 기록으로 저장
- `git branch -M main`: 로컬 브랜치 이름을 `master`에서 `main`으로 바꾸기. 요즘 GitHub의 기본 브랜치 이름이 `main`이라서 맞췄어요.

---

## 4강. GitHub에 올리기 (push)

GitHub CLI(`gh`)를 쓰면 저장소 만들기, 연결, 올리기를 한 번에 할 수 있어요.

```powershell
gh auth status   # 로그인 상태 확인
gh repo create bounce-game --public --source . --remote origin --push
```

| 옵션 | 의미 |
|---|---|
| `--public` | 공개 저장소. 무료 계정은 공개 저장소여야 Pages를 쓸 수 있어요 |
| `--source .` | 현재 폴더를 저장소로 사용 |
| `--remote origin` | 원격 저장소 이름을 `origin`으로 등록 |
| `--push` | 만들자마자 커밋을 올림 |

---

## 5강. GitHub Pages 배포

저장소 설정 화면에서 해도 되지만, 명령어 한 줄로도 할 수 있어요.

```powershell
gh api -X POST repos/enhkm/yolo26-webcam/pages -f "source[branch]=main" -f "source[path]=/"
```

- “`main` 브랜치의 최상위 폴더(`/`)를 웹사이트로 보여줘”라는 뜻이에요.
- 주소 규칙: `https://<사용자이름>.github.io/<저장소이름>/`

### 배포가 끝났는지 확인하기
Pages를 켜자마자 바로 사이트가 뜨지는 않아요. 빌드가 끝날 때까지 기다린 뒤 확인했어요.

```powershell
gh api repos/enhkm/yolo26-webcam/pages/builds/latest --jq .status   # built 가 나오면 완료
Invoke-WebRequest https://enhkm.github.io/yolo26-webcam/bounce/              # HTTP 200 이면 정상
```

---

## 6강. 오늘 만난 오류와 해결 (트러블슈팅)

### 오류 1. `node` 명령을 찾을 수 없음
**상황**: 게임 코드에 문법 오류가 없는지 Node.js로 검사하려고 `node --check`를 실행했어요.

```
node: 'node' 용어는 cmdlet, 함수, 스크립트 파일 또는 실행 프로그램의 이름으로 인식되지 않습니다.
```

**원인**: 이 PC에 Node.js가 설치되어 있지 않거나 PATH에 등록되어 있지 않아요. PowerShell은 PATH에 있는 프로그램만 이름으로 실행할 수 있어요.

**해결**: Node.js를 설치하는 대신, 이미 설치된 **Microsoft Edge를 헤드리스 모드**로 실행해서 페이지를 직접 열어 봤어요. 오히려 문법 검사보다 더 확실한 방법이에요. 실제 브라우저에서 화면이 그려지는지, 키 입력에 반응하는지까지 볼 수 있으니까요.

> 📝 배운 점: 도구가 없으면 같은 목적을 이룰 수 있는 다른 도구를 찾자. 목적은 “node 실행”이 아니라 “게임이 브라우저에서 돌아가는지 확인”이었어요.
>
> (선택) Node.js를 쓰고 싶다면 https://nodejs.org 에서 설치 후 터미널을 다시 열면 돼요.

### 오류 2. 처음 요청한 스네이크 게임 파일을 찾을 수 없음
**상황**: “아까 만든 스네이크 파일을 깃에 올려줘”라는 요청을 받고 파일을 찾았지만 없었어요.

**원인**:
- 작업 폴더에는 빈 `Initial commit` 하나만 있었고 파일이 없었어요.
- PC 전체에서 `snake`, `스네이크`, `뱀`이 들어간 파일을 검색했지만, 관련 없는 `Snakefile.smk`(유전체 분석 도구 파일) 2개만 나왔어요.
- Claude 임시 폴더와 게시된 아티팩트 목록에도 없었어요. 이전 대화에서 만든 파일이 저장되지 않았거나 다른 곳에 있었을 가능성이 커요.

**해결**: 요청이 바운스 게임으로 바뀌어서 새로 만들었어요. 스네이크 파일이 필요하면 파일 위치를 알려주세요.

> 📝 배운 점: AI와 작업한 결과물은 대화가 끝나면 사라질 수 있어요. 만든 파일은 바로 프로젝트 폴더에 저장하고 commit해 두는 습관을 들이세요.

### 참고. 경고(warning)는 오류가 아니에요
commit할 때 이런 메시지가 나왔어요.

```
warning: in the working copy of 'index.html', LF will be replaced by CRLF the next time Git touches it
```

**의미**: 줄바꿈 문자가 운영체제마다 달라요(리눅스/맥은 LF, 윈도우는 CRLF). Git이 윈도우 설정에 맞춰 나중에 바꿔줄 거라는 **안내**일 뿐이에요. 커밋은 정상으로 됐고 게임 동작에도 영향이 없어요.

### 참고. 저장소가 없다는 메시지는 의도한 확인이었어요
```
GraphQL: Could not resolve to a Repository with the name 'enhkm/bounce-game'.
```
저장소를 만들기 전에 **같은 이름의 저장소가 이미 있는지** 확인하려고 일부러 조회한 결과예요. “없다”는 답이 나왔으니 그 이름으로 새로 만들어도 된다는 뜻이에요.

---

## 복습 퀴즈
1. GitHub Pages에 올릴 첫 화면 파일의 이름은 무엇이어야 할까요?
2. 게임 루프에서 이동량에 `dt`를 곱하는 이유는 무엇일까요?
3. 무료 계정에서 Pages를 쓰려면 저장소를 공개와 비공개 중 어떻게 만들어야 할까요?
4. `node` 명령을 찾을 수 없다는 오류가 나면 어떤 원인을 의심해야 할까요?

<details>
<summary>정답 보기</summary>

1. `index.html`
2. 컴퓨터 성능(프레임 수)과 상관없이 같은 속도로 움직이게 하려고
3. 공개(public)
4. Node.js가 설치되지 않았거나 PATH에 등록되지 않음

</details>

## 다음에 해볼 것
- 3개 레벨을 직접 끝까지 플레이해 보고 난이도 조절하기
- 레벨 추가하기 (`LEVELS` 배열에 `mk(...)` 하나 더 넣기)
- 최고 기록 저장 기능 추가하기
