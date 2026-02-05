# AI Jump Rope Reference Notes

Reference repo (for algorithm idea):
- chenwr727/RopeSkippingCounter
- Key file: rope_skipping_counter.py

Key approach (summary):
- Uses MediaPipe Pose to extract hip + shoulder landmarks.
- Computes center Y (hip centroid) and shoulder-hip vertical distance.
- Maintains a buffered Y-series to smooth max/min (moving window).
- Counts a jump when center Y crosses thresholds (flip flag toggles).

Integration ideas:
- Replace direct video capture with uploaded video frames or short clips.
- Run pose estimation on server (CPU/GPU) and return:
  - reps_count
  - accuracy_score
  - issues (e.g., low light, partial body)
  - suggestions (distance, lighting, posture)
- Save training session into TrainingSession table.

Notes:
- Keep model inference separate from API (microservice or worker queue).
- Add health checks + timeout limits for video analysis.
