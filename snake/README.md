# 🐍 티처블 머신으로 조종하는 웹 뱀게임

> **강의노트** · 작성일: 2026-10-07
> 주제: 이미지 분류 AI 모델을 웹 게임의 컨트롤러로 사용하기

- 🎮 플레이: https://enhkm.github.io/yolo26-webcam/snake/
- 📦 저장소: https://github.com/enhkm/yolo26-webcam (`snake/` 폴더)

---

## 📌 학습 목표

이 수업을 마치면 다음을 할 수 있습니다.

1. **티처블 머신(Teachable Machine)** 으로 만든 이미지 분류 모델을 웹 페이지에서 불러올 수 있다.
2. 웹캠 영상을 실시간으로 모델에 넣고, **예측 결과(클래스 + 확률)** 를 읽을 수 있다.
3. HTML `<canvas>` 와 JavaScript로 **뱀게임의 기본 구조(게임 루프)** 를 이해한다.
4. AI의 예측 결과를 **게임 입력(방향키)** 으로 바꾸는 방법을 설명할 수 있다.

---

## 1. 전체 그림 한눈에 보기

```
 [웹캠] ──영상──▶ [티처블 머신 모델] ──예측──▶ [방향 결정] ──▶ [뱀게임]
                    RIGHT 0.95                 "RIGHT"         뱀이 오른쪽으로
                    LEFT  0.02
                    UP    0.02
                    DOWN  0.01
```

핵심 아이디어는 간단합니다.
**"키보드 방향키를 누르는 대신, 카메라 앞에서 동작을 하면 AI가 그걸 방향키로 바꿔준다."**

| 구성 요소 | 역할 | 사용 기술 |
|---|---|---|
| 웹캠 | 내 모습을 계속 촬영 | `tmImage.Webcam` |
| AI 모델 | 사진을 보고 RIGHT/LEFT/UP/DOWN 중 하나로 분류 | TensorFlow.js + Teachable Machine |
| 게임 | 뱀을 움직이고 먹이·충돌을 처리 | HTML Canvas + JavaScript |

---

## 2. 준비물

- 크롬(Chrome) 또는 엣지(Edge) 브라우저
- 웹캠
- 학습된 티처블 머신 **이미지 프로젝트** 모델
  - 이번 수업 모델: `https://teachablemachine.withgoogle.com/models/41OK3Sa6H/`
  - 클래스(라벨): `RIGHT`, `LEFT`, `UP`, `DOWN`
- (권장) Python — 로컬 서버를 띄우기 위해 사용

### 📂 파일 구성

```
yolo26-webcam/
└── snake/
    ├── index.html   ← 게임 + AI 연결 코드 전체 (이 파일 하나로 동작)
    └── README.md    ← 지금 보고 있는 강의노트
```

---

## 3. 실행 방법

### 3-0. 가장 쉬운 방법: GitHub Pages

👉 https://enhkm.github.io/yolo26-webcam/snake/ 에 접속하면 설치 없이 바로 플레이할 수 있습니다.
GitHub Pages는 `https://` 주소라서 웹캠도 문제없이 켜집니다.

### 3-1. 내 컴퓨터에서 실행: 로컬 서버

웹캠은 보안 때문에 `https://` 또는 `localhost` 에서 가장 안정적으로 동작합니다.

```bash
cd yolo26-webcam/snake
python -m http.server 8000
```

브라우저에서 👉 `http://localhost:8000` 접속

### 3-2. 게임 시작 순서

1. **URL로 불러오기** 버튼 클릭 (모델 주소는 미리 입력되어 있음)
2. 브라우저가 웹캠 권한을 물으면 **허용**
3. "✅ 준비 완료!" 메시지 확인
4. **시작** 버튼 또는 `Space` 키
5. 카메라 앞에서 동작을 하면 뱀이 움직입니다! (방향키로도 조작 가능)

> 💡 **모델 파일을 내려받은 경우**: 티처블 머신에서 "모델 내보내기 → 다운로드"로 받은
> `model.json`, `metadata.json`, `weights.bin` 세 파일을 선택해서 **파일로 불러오기** 를 눌러도 됩니다.

---

## 4. 1단계 — 티처블 머신 모델 만들기 (복습)

1. [teachablemachine.withgoogle.com](https://teachablemachine.withgoogle.com) → **이미지 프로젝트** → 표준 이미지 모델
2. 클래스를 4개 만들고 이름을 정확히 입력: `RIGHT`, `LEFT`, `UP`, `DOWN`
3. 각 클래스마다 웹캠으로 동작 사진을 **충분히(100장 이상 권장)** 촬영
4. **모델 학습시키기** 클릭
5. **모델 내보내기 → 업로드(공유 가능한 링크)** → 생성된 URL 복사

> ⚠️ 클래스 이름이 코드와 연결되는 "약속"입니다. 이름이 다르면 방향이 인식되지 않아요.
> (이 게임은 `DPOW` 같은 오타나 `오른쪽/왼쪽/위/아래` 같은 한글 이름도 자동으로 맞춰 줍니다.)

---

## 5. 2단계 — 웹 페이지에서 모델 불러오기

### 5-1. 라이브러리 불러오기

```html
<script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@1.3.1/dist/tf.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@teachablemachine/image@0.8/dist/teachablemachine-image.min.js"></script>
```

- `tf.min.js` : 브라우저에서 AI를 돌리는 엔진 (TensorFlow.js)
- `teachablemachine-image.min.js` : 티처블 머신 모델을 쉽게 쓰게 해주는 도구 (`tmImage`)

### 5-2. 모델 + 웹캠 준비

```js
const url = "https://teachablemachine.withgoogle.com/models/41OK3Sa6H/";
model = await tmImage.load(url + "model.json", url + "metadata.json");

webcam = new tmImage.Webcam(200, 200, true); // 가로, 세로, 좌우반전(거울모드)
await webcam.setup();   // 카메라 권한 요청
await webcam.play();    // 촬영 시작
```

> 🤔 **왜 `await` 를 쓸까?**
> 모델 다운로드, 카메라 켜기는 시간이 걸리는 작업입니다. `await` 는 "끝날 때까지 기다렸다가 다음 줄 실행"이라는 뜻입니다.

---

## 6. 3단계 — 실시간 예측하기

```js
async function loop() {
  webcam.update();           // 웹캠의 새 화면 가져오기
  await predict();           // AI에게 물어보기
  requestAnimationFrame(loop); // 다음 화면에서 또 반복
}

async function predict() {
  const prediction = await model.predict(webcam.canvas);
  // prediction 예시:
  // [ {className:"RIGHT", probability:0.95},
  //   {className:"LEFT",  probability:0.02}, ... ]
}
```

`requestAnimationFrame` 은 화면이 새로 그려질 때마다(보통 1초에 약 60번) 함수를 실행해 줍니다.
즉, **AI가 1초에 수십 번 내 동작을 확인**하는 셈입니다.

### 🎯 가장 확률이 높은 클래스 고르기 + 기준값(Threshold)

```js
let bestIdx = 0;
prediction.forEach((p, i) => {
  if (p.probability > prediction[bestIdx].probability) bestIdx = i;
});

if (prediction[bestIdx].probability >= 0.8) {   // 80% 이상 확신할 때만!
  setDirection(classDirs[bestIdx]);
}
```

> 💡 **기준값이 왜 필요할까?**
> 손을 바꾸는 중간 동작에서는 AI도 헷갈려서 확률이 40%, 35%처럼 애매하게 나옵니다.
> 이때 방향을 바꾸면 뱀이 엉뚱하게 꺾여요. 그래서 **"확실할 때만 반영"** 하는 규칙을 둡니다.
> 게임 화면의 **인식 기준 확률 슬라이더**(0.5 ~ 0.99)로 직접 조절해 보세요.

---

## 7. 4단계 — 뱀게임의 구조 이해하기

### 7-1. 게임 데이터

| 변수 | 의미 | 예시 |
|---|---|---|
| `GRID` | 판의 칸 수 | `20` (20×20 칸) |
| `snake` | 뱀 몸통 좌표 배열 (0번이 머리) | `[{x:9,y:10},{x:8,y:10},{x:7,y:10}]` |
| `dir` / `nextDir` | 현재 방향 / 다음에 바꿀 방향 | `"RIGHT"` |
| `food` | 먹이 위치 | `{x:3, y:15}` |
| `score` | 점수 | `0` |

### 7-2. 방향을 숫자로 표현하기

```js
const DIRS = {
  UP:    { x: 0,  y: -1 },   // 화면은 위로 갈수록 y가 작아짐!
  DOWN:  { x: 0,  y: 1  },
  LEFT:  { x: -1, y: 0  },
  RIGHT: { x: 1,  y: 0  },
};
```

### 7-3. 게임 루프 — `tick()` 한 번에 일어나는 일

`setInterval(tick, 130)` → 0.13초마다 아래 과정을 반복합니다.

```
① 방향 확정        dir = nextDir
② 새 머리 위치 계산  head = 머리 + 방향
③ 충돌 검사        벽 밖? 내 몸? → 게임 오버
④ 머리 추가        snake.unshift(head)
⑤ 먹이 먹었나?
     예 → 점수 +1, 새 먹이 (꼬리 유지 = 몸이 길어짐)
     아니오 → snake.pop() (꼬리 제거 = 길이 유지)
⑥ 화면 다시 그리기  draw()
```

> 🐍 **뱀이 움직이는 비밀**: 몸통 전체를 옮기는 게 아니라
> **"앞에 머리 하나 붙이고, 뒤에 꼬리 하나 떼기"** 만 하면 움직이는 것처럼 보입니다!

### 7-4. 반대 방향 금지 규칙

```js
const OPPOSITE = { UP: 'DOWN', DOWN: 'UP', LEFT: 'RIGHT', RIGHT: 'LEFT' };

function setDirection(d) {
  if (d === OPPOSITE[dir]) return;  // 오른쪽으로 가다가 바로 왼쪽 X
  nextDir = d;
}
```

오른쪽으로 가는 중 바로 왼쪽으로 꺾으면 머리가 자기 몸에 부딪히기 때문입니다.

---

## 8. 5단계 — AI와 게임 연결하기 (핵심!)

AI 예측과 게임은 **서로 다른 속도로 따로 돌아갑니다.**

| 반복 | 주기 | 하는 일 |
|---|---|---|
| AI 예측 루프 (`loop`) | 약 1/60초 | 동작을 보고 `nextDir` 만 바꿔 둠 |
| 게임 루프 (`tick`) | 0.075 ~ 0.22초 | `nextDir` 를 읽어서 뱀을 한 칸 이동 |

두 루프를 이어주는 다리가 바로 **`setDirection()`** 함수입니다.
키보드 방향키도 같은 함수를 호출하기 때문에, **AI든 키보드든 게임 입장에서는 똑같은 입력**입니다.

```js
// 키보드 입력
document.addEventListener('keydown', e => { ... setDirection('UP') ... });
// AI 입력
if (running) setDirection(d);
```

### 클래스 이름 → 방향 자동 매칭

```js
function classToDir(name) {
  const n = name.trim().toUpperCase();
  if (n.includes('RIGHT') || n.includes('오른')) return 'RIGHT';
  if (n.includes('LEFT')  || n.includes('왼'))   return 'LEFT';
  if (n.includes('UP')    || n.includes('위'))   return 'UP';
  if (n.includes('DOWN')  || n.includes('DPOW') || n.includes('아래')) return 'DOWN';
  return null;   // 그 외 클래스(예: 정지/배경)는 무시
}
```

---

## 9. 화면 구성 & 기능 정리

| 기능 | 설명 |
|---|---|
| 모델 불러오기 | 공유 URL 또는 다운로드한 파일 3개 |
| 웹캠 미리보기 | 좌우 반전(거울 모드)으로 표시 |
| 확률 막대 | 클래스별 실시간 확률, 인식된 클래스는 초록색 |
| 방향 표시 | 현재 인식된 방향을 ⬆️⬇️⬅️➡️ 로 표시 |
| 인식 기준 슬라이더 | 0.50 ~ 0.99 (기본 0.80) |
| 속도 슬라이더 | 아주 느림 ~ 아주 빠름 5단계 |
| 키보드 조작 | 방향키 / `Space` 로 시작 |
| 최고 점수 | 브라우저(localStorage)에 저장 |

---

## 10. 🛠 문제 해결 (FAQ)

| 증상 | 원인 / 해결 |
|---|---|
| 웹캠이 안 켜져요 | `index.html` 을 더블클릭해서 열었다면 → 로컬 서버(`localhost`)로 열기. 브라우저 주소창의 카메라 권한 확인 |
| 모델을 못 불러와요 | URL 끝이 `/` 로 끝나는지, 인터넷 연결 확인. 티처블 머신에서 **업로드**를 했는지 확인 |
| 방향이 자꾸 튀어요 | 인식 기준 확률을 0.9 정도로 올리기 |
| 특정 방향이 잘 안 돼요 | 그 클래스 사진을 더 다양하게(각도·거리·조명) 추가 학습 |
| 가만히 있어도 방향이 바뀌어요 | 아무 동작 없는 **"정지/배경" 클래스** 를 추가 학습 → 게임에서 자동으로 무시됨 |

---

## 11. GitHub에 올리기

이 게임은 기존 `yolo26-webcam` 저장소에 **`snake/` 폴더** 로 추가했습니다. (`bounce/` 게임과 같은 방식)

```bash
git clone https://github.com/enhkm/yolo26-webcam.git
cd yolo26-webcam
mkdir snake
# index.html, README.md 를 snake/ 폴더에 복사
git add snake
git commit -m "Add Teachable Machine webcam snake game with lecture notes"
git push
```

저장소에 GitHub Pages가 켜져 있으므로, push 후 1~2분 뒤
`https://enhkm.github.io/yolo26-webcam/snake/` 주소로 자동 배포됩니다.

> 💡 **폴더 이름 = 주소** : `snake/index.html` → `.../yolo26-webcam/snake/`
> 그래서 폴더 이름은 한글이나 띄어쓰기 없이 영어 소문자로 짓는 것이 좋습니다.

---

## 12. ✏️ 생각해 보기 & 도전 과제

**생각해 보기**
1. 기준값을 0.5로 낮추면 어떤 일이 생길까? 0.99로 올리면?
2. 웹캠 모드를 좌우 반전(`true`)하지 않으면 어떤 점이 불편할까?
3. AI 예측 루프와 게임 루프를 왜 따로 돌렸을까? 하나로 합치면 어떤 문제가 생길까?

**도전 과제** (난이도 순)
- ⭐ 먹이 색깔이나 뱀 색깔 바꾸기 (`draw()` 함수의 `fillStyle`)
- ⭐ 판 크기 바꾸기 (`GRID` 값)
- ⭐⭐ 먹이를 먹을수록 점점 빨라지게 만들기
- ⭐⭐ 벽에 부딪히면 반대편에서 나오게 바꾸기
- ⭐⭐⭐ "STOP" 클래스를 학습시켜 일시정지 기능 추가하기
- ⭐⭐⭐ 같은 방향이 3번 연속 인식될 때만 반영해서 오인식 줄이기

---

## 13. 📝 오늘 배운 내용 요약

- **티처블 머신** 모델은 `tmImage.load()` 로 웹에서 바로 불러올 수 있다.
- `model.predict()` 는 **각 클래스의 확률** 을 돌려준다 → 가장 높은 것을 고른다.
- **기준값(Threshold)** 으로 애매한 예측을 걸러내야 게임이 안정적이다.
- 뱀게임은 **"머리 추가 + 꼬리 제거"** 를 일정 시간마다 반복하는 게임 루프다.
- AI 입력과 키보드 입력을 **같은 함수(`setDirection`)** 로 처리하면 구조가 깔끔해진다.
- 폴더째 GitHub에 올리면 **GitHub Pages** 로 누구나 https 주소에서 웹캠 게임을 할 수 있다.
