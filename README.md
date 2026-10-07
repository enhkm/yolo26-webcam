# YOLO26으로 배우는 웹캠 실시간 비전 AI

> **강의 노트** · 작성일 2026-10-07
> Ultralytics **YOLO26** 모델 하나로 웹캠 영상에서 **객체 탐지(Detection) → 객체 분할(Segmentation) → 객체 추적(Tracking)** 까지 단계별로 구현해 봅니다.

---

## 목차

0. [학습 목표](#0-학습-목표)
1. [개념 정리: 탐지 · 분할 · 추적](#1-개념-정리-탐지--분할--추적)
2. [실습 환경 준비](#2-실습-환경-준비)
3. [실습 1: Object Detection](#3-실습-1-object-detection)
4. [실습 2: Instance Segmentation](#4-실습-2-instance-segmentation)
5. [실습 3: Object Tracking](#5-실습-3-object-tracking)
6. [세 코드 비교 한눈에 보기](#6-세-코드-비교-한눈에-보기)
7. [트러블슈팅: 오늘 실제로 만난 문제들](#7-트러블슈팅-오늘-실제로-만난-문제들)
8. [GitHub에 올리기](#8-github에-올리기)
9. [연습 문제](#9-연습-문제)
10. [오늘의 요약](#10-오늘의-요약)

---

## 0. 학습 목표

이 강의를 마치면 다음을 할 수 있습니다.

- [ ] 탐지(Detection), 분할(Segmentation), 추적(Tracking)의 차이를 설명할 수 있다.
- [ ] OpenCV로 웹캠 프레임을 읽고 화면에 띄우는 기본 루프를 작성할 수 있다.
- [ ] Ultralytics `YOLO` 클래스로 모델을 불러와 `predict()`와 `track()`을 호출할 수 있다.
- [ ] 결과 객체(`Results`)에서 박스, 클래스, 마스크, 트랙 ID를 꺼내 활용할 수 있다.
- [ ] 작업한 코드를 GitHub 저장소로 정리해 공유할 수 있다.

---

## 1. 개념 정리: 탐지 · 분할 · 추적

| 작업 | 질문 | 출력 | 사용 모델 |
|---|---|---|---|
| **Object Detection** | 무엇이 **어디에** 있나? | 사각형 박스 + 클래스 + 신뢰도 | `yolo26n.pt` |
| **Instance Segmentation** | 그 물체의 **정확한 모양**은? | 박스 + 픽셀 단위 마스크 | `yolo26n-seg.pt` |
| **Object Tracking** | 이전 프레임의 그 물체가 **지금 어디** 있나? | 박스 + **고유 ID** (프레임 간 유지) | `yolo26n.pt` + 트래커 |

```
Detection       Segmentation       Tracking
┌───────┐       ┌───────┐          ┌─id:1──┐   ┌─id:1──┐
│ person│       │ ▓▓▓▓▓ │          │ person│ → │ person│   ← 같은 사람 = 같은 ID
│       │       │▓▓▓▓▓▓▓│          │       │   │       │
└───────┘       └───────┘          └───────┘   └───────┘
  박스만          모양까지            frame t      frame t+1
```

> 💡 **핵심 포인트**
> - 분할은 탐지의 **확장**입니다. 박스에 더해 마스크를 추가로 예측합니다.
> - 추적은 **새 모델이 아니라** 탐지 결과에 트래커 알고리즘(ByteTrack, BoT-SORT)을 붙인 것입니다. 그래서 탐지 모델과 분할 모델 모두로 추적할 수 있습니다.

### YOLO26 모델 크기

같은 작업이라도 모델 크기를 고를 수 있습니다. 파일 이름의 알파벳이 크기를 나타냅니다.

```
yolo26n  <  yolo26s  <  yolo26m  <  yolo26l  <  yolo26x
(nano)                                          (extra large)
 빠름 ◀───────────────────────────────────────▶ 정확함
```

분할 모델은 이름 끝에 `-seg`가 붙습니다 (예: `yolo26s-seg.pt`).
웹캠 실시간 실습에서는 **CPU로도 돌아가는 `n`(nano)** 을 기본으로 사용했습니다.

---

## 2. 실습 환경 준비

### 2-1. 실습에 사용한 환경

| 항목 | 버전 |
|---|---|
| OS | Windows 11 |
| Python | 3.14 |
| ultralytics | 8.4.x |
| torch | 2.14 (CPU) |
| opencv-python | 5.0 |

### 2-2. 패키지 설치

```bash
pip install -r requirements.txt
```

`requirements.txt` 내용:

```
ultralytics>=8.4.0
opencv-python
```

> 📝 `ultralytics`를 설치하면 `torch`, `torchvision` 등 필요한 패키지가 함께 설치됩니다.
> 모델 가중치 파일(`.pt`)은 **처음 실행할 때 자동으로 다운로드**되므로 따로 받을 필요가 없습니다.

### 2-3. 설치 확인

```bash
python -c "import torch, cv2; print(torch.__version__, cv2.__version__)"
```

Windows에서 이 단계에서 `WinError 126` 오류가 난다면 → [7장 트러블슈팅](#7-트러블슈팅-오늘-실제로-만난-문제들)을 보세요.

---

## 3. 실습 1: Object Detection

📄 파일: [`webcam_detect.py`](webcam_detect.py)

### 3-1. 전체 흐름

모든 실습 코드는 아래 **5단계 루프**를 공유합니다. 이 구조를 먼저 익혀 두면 2, 3번 실습은 "바뀐 부분"만 보면 됩니다.

```
① 모델 불러오기  →  ② 웹캠 열기  →  ┌─▶ ③ 프레임 읽기
                                   │   ④ 추론 + 결과 그리기
                                   └── ⑤ 화면 표시 / 종료 키 확인
```

### 3-2. 단계별 코드 해설

**① 모델 불러오기**

```python
from ultralytics import YOLO

model = YOLO("yolo26n.pt")   # 파일이 없으면 자동 다운로드
```

**② 웹캠 열기**

```python
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)   # 0번 카메라, Windows용 DirectShow 백엔드
if not cap.isOpened():
    cap = cv2.VideoCapture(0)              # 실패하면 기본 백엔드로 재시도
```

> 💡 `cv2.CAP_DSHOW`는 Windows에서 웹캠을 더 빠르고 안정적으로 열어 줍니다. 다른 OS에서는 기본 백엔드로 넘어갑니다.

**③ 프레임 읽기**

```python
ok, frame = cap.read()   # ok: 성공 여부, frame: BGR 이미지 (numpy 배열)
```

**④ 추론 + 결과 그리기**

```python
results = model.predict(frame, conf=0.25, imgsz=640, verbose=False)
result = results[0]          # 이미지 1장을 넣었으므로 결과도 1개
annotated = result.plot()    # 박스·클래스명·신뢰도를 그린 이미지 반환
```

| 인자 | 의미 |
|---|---|
| `conf` | 이 값보다 신뢰도가 낮은 탐지는 버림 |
| `imgsz` | 모델에 넣을 이미지 크기 (클수록 작은 물체에 강하지만 느림) |
| `verbose=False` | 매 프레임 콘솔 로그 끄기 |

**결과에서 정보 꺼내기** — 클래스별 개수 세기:

```python
names = result.names                          # {0: 'person', 1: 'bicycle', ...}
for cls_id in result.boxes.cls.int().tolist():
    label = names[cls_id]
    counts[label] = counts.get(label, 0) + 1
```

> 📝 `result.boxes`에서 자주 쓰는 속성
> - `boxes.xyxy` : 좌상단·우하단 좌표 `[x1, y1, x2, y2]`
> - `boxes.xywh` : 중심 좌표와 크기 `[cx, cy, w, h]`
> - `boxes.cls`  : 클래스 번호
> - `boxes.conf` : 신뢰도

**⑤ 화면 표시 / 종료**

```python
cv2.imshow(window, annotated)
key = cv2.waitKey(1) & 0xFF
if key in (ord("q"), 27):        # q 또는 ESC
    break
```

마지막에는 `finally` 블록에서 `cap.release()`와 `cv2.destroyAllWindows()`로 자원을 반드시 정리합니다.

### 3-3. 실행

```bash
python webcam_detect.py
python webcam_detect.py --model yolo26s.pt --conf 0.4
```

✅ **기대 결과**: 사람·물체에 박스와 라벨이 그려지고, 왼쪽 위에 FPS와 클래스별 개수가 표시됩니다.

---

## 4. 실습 2: Instance Segmentation

📄 파일: [`webcam_segment.py`](webcam_segment.py)

### 4-1. 실습 1과 달라진 점 (딱 3곳)

```diff
- model = YOLO("yolo26n.pt")
+ model = YOLO("yolo26n-seg.pt")          # ① 분할 전용 모델

  results = model.predict(
      frame,
      conf=args.conf,
+     retina_masks=True,                  # ② 마스크를 원본 해상도로
      verbose=False,
  )
- annotated = result.plot()
+ annotated = result.plot(boxes=not args.no_boxes, masks=True)   # ③ 마스크 그리기
```

| 변경 | 설명 |
|---|---|
| `-seg` 모델 | 박스와 함께 마스크를 예측하는 모델 |
| `retina_masks=True` | 기본 마스크는 저해상도라 경계가 계단처럼 보임 → 원본 크기로 출력해 매끄럽게 |
| `plot(boxes=..., masks=True)` | 박스 표시 여부를 선택 (`--no-boxes` 옵션) |

### 4-2. 마스크 데이터 살펴보기

```python
result.masks.data.shape   # (객체 수, 높이, 너비) 예: (2, 480, 640)
```

각 객체마다 프레임과 같은 크기의 0/1 마스크가 하나씩 들어 있습니다.
실습 중 프레임 한 장으로 확인한 결과 `(2, 480, 640)` — 즉 **객체 2개**에 대한 마스크가 나왔습니다.

### 4-3. 실행

```bash
python webcam_segment.py
python webcam_segment.py --no-boxes      # 마스크만 표시
```

✅ **기대 결과**: 객체마다 서로 다른 색의 반투명 마스크가 덮입니다.

---

## 5. 실습 3: Object Tracking

📄 파일: [`webcam_track.py`](webcam_track.py)

### 5-1. 핵심: `predict()` → `track()`

```diff
- results = model.predict(frame, ...)
+ results = model.track(
+     frame,
+     persist=True,                 # ⭐ 이전 프레임 정보를 기억
+     tracker="bytetrack.yaml",     # 사용할 트래커
+     ...
+ )
```

> ⚠️ **`persist=True`를 빼먹으면?**
> 매 프레임을 새 영상의 첫 프레임으로 취급해서 **ID가 계속 새로 발급**됩니다. 웹캠처럼 프레임을 하나씩 넣는 경우 반드시 `True`로 설정하세요.

### 5-2. 트래커 선택

| 트래커 | 특징 |
|---|---|
| `bytetrack.yaml` (기본) | 빠름. 신뢰도가 낮은 박스까지 활용해 가려진 객체도 잘 이어 붙임 |
| `botsort.yaml` | 조금 느리지만 카메라 움직임 보정 등으로 ID가 덜 바뀜 |

### 5-3. 트랙 ID 꺼내기

```python
boxes = result.boxes
if boxes.id is not None:                       # 추적 대상이 없으면 None
    ids = boxes.id.int().tolist()              # 예: [1, 2, 3]
    for (x, y, w, h), track_id in zip(boxes.xywh.tolist(), ids):
        ...
```

> 📝 탐지 결과에는 없던 **`boxes.id`** 가 추적에서 새로 생기는 속성입니다.

### 5-4. 이동 궤적 그리기

ID별로 박스 중심점을 `deque`에 쌓아 두고 선으로 잇습니다.

```python
from collections import defaultdict, deque

trails = defaultdict(lambda: deque(maxlen=30))   # 최근 30개 점만 유지

trail = trails[track_id]
trail.append((int(x), int(y)))                   # 박스 중심점
for i in range(1, len(trail)):
    thickness = max(1, int(4 * i / len(trail)))  # 최근일수록 굵게
    cv2.line(annotated, trail[i - 1], trail[i], color, thickness)
```

| 기법 | 이유 |
|---|---|
| `deque(maxlen=30)` | 오래된 점은 자동으로 버려져 메모리가 늘지 않음 |
| `color_for_id(track_id)` | ID로 색을 계산 → 같은 객체는 항상 같은 색 |
| 사라진 ID 삭제 | 화면에서 없어진 객체의 궤적이 남지 않도록 정리 |

### 5-5. 실습 중 확인한 결과

프레임 10장으로 테스트한 ID 변화:

```
frame 0 ids [1, 2]
frame 1 ids [1, 2]
frame 2 ids [1, 2]
frame 3 ids [1, 2, 3]   ← 새 객체 등장 → 새 ID 3 발급
...
frame 9 ids [1, 2, 3]   ← 기존 객체는 ID 유지
```

### 5-6. 실행

```bash
python webcam_track.py
python webcam_track.py --tracker botsort.yaml --trail 50
python webcam_track.py --model yolo26n-seg.pt    # 분할 + 추적 동시에!
```

✅ **기대 결과**: 라벨에 `id:1 person 0.89`처럼 ID가 붙고, 움직이면 색깔 궤적이 따라옵니다.

---

## 6. 세 코드 비교 한눈에 보기

| | Detection | Segmentation | Tracking |
|---|---|---|---|
| 모델 | `yolo26n.pt` | `yolo26n-seg.pt` | `yolo26n.pt` |
| 호출 | `model.predict()` | `model.predict(retina_masks=True)` | `model.track(persist=True)` |
| 새로 얻는 정보 | `boxes` | `masks` | `boxes.id` |
| 화면 추가 정보 | 클래스별 개수 | 클래스별 개수 | 현재 추적 수 / 누적 ID 수 / 궤적 |
| 전용 옵션 | – | `--no-boxes` | `--tracker`, `--trail` |

### 공통 옵션

| 옵션 | 기본값 | 설명 |
|---|---|---|
| `--model` | 스크립트별 상이 | 모델 파일 (`n`/`s`/`m`/`l`/`x`) |
| `--camera` | `0` | 웹캠 번호 (여러 대면 `1`, `2`…) |
| `--conf` | `0.25` | 신뢰도 임계값 |
| `--imgsz` | `640` | 추론 이미지 크기 |
| `--device` | 자동 | `cpu` 또는 GPU 번호(`0`) |

종료: 영상 창에서 **`q`** 또는 **`ESC`**

---

## 7. 트러블슈팅: 오늘 실제로 만난 문제들

### 문제 1. `ModuleNotFoundError: No module named 'ultralytics'`

- **원인**: 패키지 미설치
- **해결**: `pip install -U ultralytics opencv-python`

### 문제 2. `OSError: [WinError 126] ... c10.dll`

```
OSError: [WinError 126] 지정된 모듈을 찾을 수 없습니다.
Error loading "...\torch\lib\c10.dll" or one of its dependencies.
Microsoft Visual C++ Redistributable is not installed
```

- **원인**: Windows에 **Microsoft Visual C++ 재배포 패키지**가 없어 PyTorch DLL을 불러오지 못함. 코드 문제가 아님!
- **해결**: 아래 중 하나로 설치 후 다시 실행
  - 직접 다운로드: https://aka.ms/vs/17/release/vc_redist.x64.exe
  - 명령어: `winget install Microsoft.VCRedist.2015+.x64`

### 문제 3. 트래킹 첫 실행 시 `lap` 패키지 자동 설치

```
requirements: AutoUpdate success
WARNING requirements: Restart runtime or rerun command for updates to take effect
```

- **원인**: ByteTrack이 사용하는 `lap` 패키지를 Ultralytics가 자동으로 설치
- **해결**: 정상 동작입니다. 경고가 나오면 한 번 다시 실행하세요.

### 문제 4. 해상도를 1280×720으로 설정했는데 640×480으로 나옴

```python
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
```

- **원인**: `cap.set()`은 **요청**일 뿐, 웹캠이 지원하지 않으면 무시됨
- **확인**: `frame.shape`로 실제 크기 확인
- **해결**: 동작에는 문제 없음. 고해상도가 필요하면 지원하는 웹캠 사용

### 문제 5. GPU가 있는데 CPU로 돌아감

- **원인**: 기본 설치되는 `torch`가 CPU 전용 버전일 수 있음 (`torch.cuda.is_available()` → `False`)
- **해결**: [PyTorch 공식 사이트](https://pytorch.org/get-started/locally/)에서 CUDA 버전 설치 후 `--device 0`

---

## 8. GitHub에 올리기

### 8-1. 저장소 구성

```
yolo26-webcam/
├── README.md            # 이 강의 노트
├── requirements.txt     # 필요한 패키지
├── .gitignore           # 업로드에서 제외할 파일
├── webcam_detect.py     # 실습 1
├── webcam_segment.py    # 실습 2
└── webcam_track.py      # 실습 3
```

### 8-2. `.gitignore`로 모델 파일 제외하기

```gitignore
# 모델 가중치 (실행 시 자동 다운로드되므로 올리지 않음)
*.pt

# Ultralytics 출력 폴더
runs/

__pycache__/
```

> ⚠️ `.gitignore`에서 주석은 **줄 맨 앞의 `#`** 만 인정됩니다. `*.pt  # 설명`처럼 같은 줄에 쓰면 패턴이 깨집니다.

> 💡 모델 파일은 용량이 크고 언제든 다시 받을 수 있으므로 저장소에 올리지 않는 것이 관례입니다.

### 8-3. 업로드 명령어

```bash
git init -b main
git add .
git commit -m "Add YOLO26 webcam detection, segmentation, and tracking examples"
gh repo create yolo26-webcam --public --source . --push
```

### 8-4. 이후 수정 사항 반영

```bash
git add .
git commit -m "변경 내용 설명"
git push
```

---

## 9. 연습 문제

난이도: ⭐ 쉬움 · ⭐⭐ 보통 · ⭐⭐⭐ 도전

1. ⭐ `webcam_detect.py`를 `yolo26s.pt`로 바꿔 실행하고, `n` 모델과 FPS·정확도를 비교해 보세요.
2. ⭐ `--conf` 값을 `0.1`, `0.5`, `0.8`로 바꿔 가며 탐지 결과가 어떻게 달라지는지 관찰하세요.
3. ⭐⭐ **사람(person)만** 탐지하도록 바꿔 보세요.
   <details><summary>힌트</summary>

   `model.predict(..., classes=[0])` — COCO 데이터셋에서 `person`의 클래스 번호는 `0`입니다.
   </details>
4. ⭐⭐ 세그멘테이션 마스크를 이용해 **사람만 남기고 배경을 검게** 만들어 보세요.
   <details><summary>힌트</summary>

   `result.masks.data`의 마스크들을 합쳐 `frame`에 곱하세요. `retina_masks=True`이면 프레임과 크기가 같습니다.
   </details>
5. ⭐⭐ 결과 영상을 `output.mp4`로 저장하는 기능을 추가하세요.
   <details><summary>힌트</summary>

   `cv2.VideoWriter("output.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 20, (w, h))`
   </details>
6. ⭐⭐⭐ 화면 가운데에 가상의 선을 긋고, 트래킹 ID를 이용해 **선을 넘어간 사람 수**를 세어 보세요.
   <details><summary>힌트</summary>

   ID별로 이전 프레임의 중심 y 좌표를 기억해 두고, 선의 위·아래가 바뀐 순간을 감지하세요. 같은 ID는 한 번만 세도록 `set`을 활용합니다.
   </details>

---

## 10. 오늘의 요약

- **YOLO26** 하나로 `predict` / `track` 호출과 모델 파일만 바꿔 탐지 · 분할 · 추적을 모두 구현했다.
- 세 코드는 **같은 웹캠 루프 구조**(모델 → 웹캠 → 프레임 → 추론 → 표시)를 공유한다.
- 분할은 `-seg` 모델 + `retina_masks=True`, 추적은 `track(persist=True)`가 핵심이다.
- Windows에서 PyTorch DLL 오류는 **Visual C++ 재배포 패키지** 설치로 해결한다.
- 모델 가중치는 `.gitignore`로 제외하고 코드만 GitHub에 올린다.

---

### 참고 자료

- Ultralytics 공식 문서: https://docs.ultralytics.com
- Predict 모드: https://docs.ultralytics.com/modes/predict/
- Track 모드: https://docs.ultralytics.com/modes/track/
- Segmentation 작업: https://docs.ultralytics.com/tasks/segment/
