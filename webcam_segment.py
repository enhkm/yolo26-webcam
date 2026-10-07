"""
Ultralytics YOLO26 웹캠 실시간 Instance Segmentation

설치:
    pip install -U ultralytics opencv-python

실행:
    python webcam_segment.py
    python webcam_segment.py --model yolo26s-seg.pt --conf 0.4 --camera 0

종료: 영상 창에서 'q' 또는 ESC
"""
import argparse
import time

import cv2
from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(description="YOLO26 webcam instance segmentation")
    parser.add_argument("--model", default="yolo26n-seg.pt",
                        help="세그멘테이션 모델 (yolo26n/s/m/l/x-seg.pt), 없으면 자동 다운로드")
    parser.add_argument("--camera", type=int, default=0, help="웹캠 인덱스")
    parser.add_argument("--conf", type=float, default=0.25, help="confidence threshold")
    parser.add_argument("--imgsz", type=int, default=640, help="추론 이미지 크기")
    parser.add_argument("--device", default=None, help="예: 'cpu', '0' (GPU)")
    parser.add_argument("--no-boxes", action="store_true", help="박스는 숨기고 마스크만 표시")
    return parser.parse_args()


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

    window = "YOLO26 Webcam Segmentation"
    prev_time = time.time()

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("프레임을 읽지 못했습니다.")
                break

            results = model.predict(
                frame,
                conf=args.conf,
                imgsz=args.imgsz,
                device=args.device,
                retina_masks=True,  # 마스크를 원본 해상도로 출력해 경계를 매끄럽게
                verbose=False,
            )
            result = results[0]
            # 마스크(반투명 색상) + 박스 + 클래스명 + 점수 그리기
            annotated = result.plot(boxes=not args.no_boxes, masks=True)

            # 클래스별 객체 수 집계
            names = result.names
            counts = {}
            if result.boxes is not None:
                for cls_id in result.boxes.cls.int().tolist():
                    label = names[cls_id]
                    counts[label] = counts.get(label, 0) + 1

            # FPS 계산
            now = time.time()
            fps = 1.0 / max(now - prev_time, 1e-6)
            prev_time = now

            cv2.putText(annotated, f"FPS: {fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            summary = ", ".join(f"{k}: {v}" for k, v in counts.items())
            if summary:
                cv2.putText(annotated, summary, (10, 65),
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
