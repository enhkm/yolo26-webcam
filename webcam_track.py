"""
Ultralytics YOLO26 웹캠 실시간 Object Tracking

설치:
    pip install -U ultralytics opencv-python

실행:
    python webcam_track.py
    python webcam_track.py --tracker botsort.yaml --conf 0.4 --camera 0

종료: 영상 창에서 'q' 또는 ESC
"""
import argparse
import time
from collections import defaultdict, deque

import cv2
from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(description="YOLO26 webcam object tracking")
    parser.add_argument("--model", default="yolo26n.pt",
                        help="모델 파일 (yolo26n/s/m/l/x.pt, -seg 모델도 가능), 없으면 자동 다운로드")
    parser.add_argument("--tracker", default="bytetrack.yaml",
                        help="트래커 설정 (bytetrack.yaml 또는 botsort.yaml)")
    parser.add_argument("--camera", type=int, default=0, help="웹캠 인덱스")
    parser.add_argument("--conf", type=float, default=0.25, help="confidence threshold")
    parser.add_argument("--imgsz", type=int, default=640, help="추론 이미지 크기")
    parser.add_argument("--device", default=None, help="예: 'cpu', '0' (GPU)")
    parser.add_argument("--trail", type=int, default=30, help="이동 궤적으로 남길 프레임 수 (0이면 끔)")
    return parser.parse_args()


def color_for_id(track_id):
    # ID마다 고정된 색을 쓰도록 ID로 색을 만든다
    return ((track_id * 37) % 255, (track_id * 17) % 255, (track_id * 97) % 255)


def main():
    args = parse_args()

    model = YOLO(args.model)

    # Windows에서는 CAP_DSHOW가 웹캠을 더 빠르고 안정적으로 엽니다
    cap = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        raise RuntimeError(f"웹캠을 열 수 없습니다 (index={args.camera})")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    window = "YOLO26 Webcam Tracking"
    trails = defaultdict(lambda: deque(maxlen=max(args.trail, 1)))  # track_id -> 중심점 기록
    seen_ids = set()
    prev_time = time.time()

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("프레임을 읽지 못했습니다.")
                break

            # persist=True: 이전 프레임의 트랙 정보를 유지해서 같은 객체에 같은 ID를 부여
            results = model.track(
                frame,
                persist=True,
                tracker=args.tracker,
                conf=args.conf,
                imgsz=args.imgsz,
                device=args.device,
                verbose=False,
            )
            result = results[0]
            annotated = result.plot()  # 박스 + 클래스명 + ID + 점수 그리기

            # 트랙 ID별 이동 궤적 그리기
            boxes = result.boxes
            if boxes is not None and boxes.id is not None:
                ids = boxes.id.int().tolist()
                for (x, y, w, h), track_id in zip(boxes.xywh.tolist(), ids):
                    seen_ids.add(track_id)
                    if args.trail <= 0:
                        continue
                    trail = trails[track_id]
                    trail.append((int(x), int(y)))
                    color = color_for_id(track_id)
                    for i in range(1, len(trail)):
                        thickness = max(1, int(4 * i / len(trail)))
                        cv2.line(annotated, trail[i - 1], trail[i], color, thickness)

                # 화면에서 사라진 ID의 궤적은 정리
                for track_id in list(trails):
                    if track_id not in ids:
                        del trails[track_id]
                current = len(ids)
            else:
                trails.clear()
                current = 0

            # FPS 계산
            now = time.time()
            fps = 1.0 / max(now - prev_time, 1e-6)
            prev_time = now

            cv2.putText(annotated, f"FPS: {fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            cv2.putText(annotated, f"Tracking: {current}  Total IDs: {len(seen_ids)}", (10, 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            cv2.imshow(window, annotated)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if cv2.getWindowProperty(window, cv2.WND_PROP_VISIBLE) < 1:
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
