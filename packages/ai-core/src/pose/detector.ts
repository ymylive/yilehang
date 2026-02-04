/**
 * 姿态检测器 - 基于MediaPipe Pose
 * 用于前端实时姿态检测
 */

export interface Point {
  x: number
  y: number
  z: number
  visibility: number
}

export interface PoseLandmarks {
  landmarks: Point[]
}

// MediaPipe关键点索引
export const POSE_LANDMARKS = {
  NOSE: 0,
  LEFT_EYE_INNER: 1,
  LEFT_EYE: 2,
  LEFT_EYE_OUTER: 3,
  RIGHT_EYE_INNER: 4,
  RIGHT_EYE: 5,
  RIGHT_EYE_OUTER: 6,
  LEFT_EAR: 7,
  RIGHT_EAR: 8,
  MOUTH_LEFT: 9,
  MOUTH_RIGHT: 10,
  LEFT_SHOULDER: 11,
  RIGHT_SHOULDER: 12,
  LEFT_ELBOW: 13,
  RIGHT_ELBOW: 14,
  LEFT_WRIST: 15,
  RIGHT_WRIST: 16,
  LEFT_PINKY: 17,
  RIGHT_PINKY: 18,
  LEFT_INDEX: 19,
  RIGHT_INDEX: 20,
  LEFT_THUMB: 21,
  RIGHT_THUMB: 22,
  LEFT_HIP: 23,
  RIGHT_HIP: 24,
  LEFT_KNEE: 25,
  RIGHT_KNEE: 26,
  LEFT_ANKLE: 27,
  RIGHT_ANKLE: 28,
  LEFT_HEEL: 29,
  RIGHT_HEEL: 30,
  LEFT_FOOT_INDEX: 31,
  RIGHT_FOOT_INDEX: 32
}

export class PoseDetector {
  private pose: any = null
  private camera: any = null
  private isInitialized = false
  private onResultsCallback: ((landmarks: PoseLandmarks) => void) | null = null

  /**
   * 初始化姿态检测器
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) return

    // 动态导入MediaPipe
    const { Pose } = await import('@mediapipe/pose')

    this.pose = new Pose({
      locateFile: (file: string) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`
      }
    })

    this.pose.setOptions({
      modelComplexity: 1,
      smoothLandmarks: true,
      enableSegmentation: false,
      smoothSegmentation: false,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5
    })

    this.pose.onResults((results: any) => {
      if (results.poseLandmarks && this.onResultsCallback) {
        this.onResultsCallback({
          landmarks: results.poseLandmarks
        })
      }
    })

    this.isInitialized = true
  }

  /**
   * 启动摄像头检测
   */
  async startCamera(
    videoElement: HTMLVideoElement,
    onResults: (landmarks: PoseLandmarks) => void
  ): Promise<void> {
    await this.initialize()

    this.onResultsCallback = onResults

    const { Camera } = await import('@mediapipe/camera_utils')

    this.camera = new Camera(videoElement, {
      onFrame: async () => {
        await this.pose.send({ image: videoElement })
      },
      width: 640,
      height: 480
    })

    await this.camera.start()
  }

  /**
   * 停止检测
   */
  stop(): void {
    if (this.camera) {
      this.camera.stop()
      this.camera = null
    }
    this.onResultsCallback = null
  }

  /**
   * 计算三点角度
   */
  static calculateAngle(p1: Point, p2: Point, p3: Point): number {
    const v1 = { x: p1.x - p2.x, y: p1.y - p2.y }
    const v2 = { x: p3.x - p2.x, y: p3.y - p2.y }

    const dot = v1.x * v2.x + v1.y * v2.y
    const mag1 = Math.sqrt(v1.x * v1.x + v1.y * v1.y)
    const mag2 = Math.sqrt(v2.x * v2.x + v2.y * v2.y)

    const cosAngle = Math.max(-1, Math.min(1, dot / (mag1 * mag2 + 1e-6)))
    return Math.acos(cosAngle) * (180 / Math.PI)
  }

  /**
   * 计算两点距离
   */
  static calculateDistance(p1: Point, p2: Point): number {
    return Math.sqrt(Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2))
  }

  /**
   * 获取膝关节角度
   */
  static getKneeAngle(landmarks: PoseLandmarks, side: 'left' | 'right'): number {
    const hip = side === 'left'
      ? landmarks.landmarks[POSE_LANDMARKS.LEFT_HIP]
      : landmarks.landmarks[POSE_LANDMARKS.RIGHT_HIP]
    const knee = side === 'left'
      ? landmarks.landmarks[POSE_LANDMARKS.LEFT_KNEE]
      : landmarks.landmarks[POSE_LANDMARKS.RIGHT_KNEE]
    const ankle = side === 'left'
      ? landmarks.landmarks[POSE_LANDMARKS.LEFT_ANKLE]
      : landmarks.landmarks[POSE_LANDMARKS.RIGHT_ANKLE]

    return this.calculateAngle(hip, knee, ankle)
  }

  /**
   * 获取肘关节角度
   */
  static getElbowAngle(landmarks: PoseLandmarks, side: 'left' | 'right'): number {
    const shoulder = side === 'left'
      ? landmarks.landmarks[POSE_LANDMARKS.LEFT_SHOULDER]
      : landmarks.landmarks[POSE_LANDMARKS.RIGHT_SHOULDER]
    const elbow = side === 'left'
      ? landmarks.landmarks[POSE_LANDMARKS.LEFT_ELBOW]
      : landmarks.landmarks[POSE_LANDMARKS.RIGHT_ELBOW]
    const wrist = side === 'left'
      ? landmarks.landmarks[POSE_LANDMARKS.LEFT_WRIST]
      : landmarks.landmarks[POSE_LANDMARKS.RIGHT_WRIST]

    return this.calculateAngle(shoulder, elbow, wrist)
  }
}

export default PoseDetector
