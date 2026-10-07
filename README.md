# YOLO26 Webcam

[Ultralytics](https://github.com/ultralytics/ultralytics) **YOLO26** 모델로 웹캠 영상을 실시간 처리하는 Python 예제 모음입니다.

| 파일 | 기능 | 기본 모델 |
|---|---|---|
| [`webcam_detect.py`](webcam_detect.py) | Object Detection (객체 탐지) | `yolo26n.pt` |
| [`webcam_segment.py`](webcam_segment.py) | Instance Segmentation (객체 분할) | `yolo26n-seg.pt` |
| [`webcam_track.py`](webcam_track.py) | Object Tracking (객체 추적) | `yolo26n.pt` |

모델 파일은 처음 실행할 때 자동으로 다운로드됩니다.

## 설치

```bash
pip install -r requirements.txt
```

> **Windows**에서 `torch` 임포트 시 `WinError 126 ... c10.dll` 오류가 나면
> [Microsoft Visual C++ 재배포 패키지](https://aka.ms/vs/17/release/vc_redist.x64.exe)를 설치하세요.
> (`winget install Microsoft.VCRedist.2015+.x64`)

## 사용법

공통으로 영상 창에서 `q` 또는 `ESC`를 누르면 종료됩니다.

### 1. Object Detection

```bash
python webcam_detect.py
python webcam_detect.py --model yolo26s.pt --conf 0.4 --camera 0
```

탐지된 객체에 박스, 클래스명, 신뢰도를 표시하고 화면 왼쪽 위에 FPS와 클래스별 개수를 보여줍니다.

### 2. Instance Segmentation

```bash
python webcam_segment.py
python webcam_segment.py --no-boxes --conf 0.4
```

객체마다 반투명 색상 마스크를 씌웁니다. `retina_masks=True`로 마스크를 원본 해상도로 출력해 경계가 매끄럽습니다.

### 3. Object Tracking

```bash
python webcam_track.py
python webcam_track.py --tracker botsort.yaml --trail 50
python webcam_track.py --model yolo26n-seg.pt   # 세그멘테이션 + 트래킹
```

`model.track(persist=True)`로 프레임 간 같은 객체에 같은 ID를 부여하고, ID별 이동 궤적을 그립니다.
화면에 현재 추적 중인 객체 수와 누적 ID 수를 표시합니다.

## 옵션

| 옵션 | 기본값 | 설명 | 적용 |
|---|---|---|---|
| `--model` | `yolo26n.pt` / `yolo26n-seg.pt` | 모델 크기: `n` < `s` < `m` < `l` < `x` (클수록 정확, 느림) | 전체 |
| `--camera` | `0` | 웹캠 인덱스 | 전체 |
| `--conf` | `0.25` | 신뢰도 임계값 | 전체 |
| `--imgsz` | `640` | 추론 이미지 크기 | 전체 |
| `--device` | 자동 | `cpu` 또는 GPU 번호(`0`) | 전체 |
| `--no-boxes` | - | 박스 숨기고 마스크만 표시 | segment |
| `--tracker` | `bytetrack.yaml` | `bytetrack.yaml`(빠름) / `botsort.yaml`(ID 안정적) | track |
| `--trail` | `30` | 궤적으로 남길 프레임 수 (`0`이면 끔) | track |
