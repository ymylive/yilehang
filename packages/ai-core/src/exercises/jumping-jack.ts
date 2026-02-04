/**
 * 运动计数器 - 开合跳
 */
import { PoseLandmarks, PoseDetector, POSE_LANDMARKS } from '../pose/detector'
import { ExerciseResult } from './squat'

export class JumpingJackCounter {
  private count = 0
  private state: 'idle' | 'up' | 'down' = 'idle'
  private prevFeetDistance = 0

  analyze(landmarks: PoseLandmarks): ExerciseResult {
    const leftAnkle = landmarks.landmarks[POSE_LANDMARKS.LEFT_ANKLE]
    const rightAnkle = landmarks.landmarks[POSE_LANDMARKS.RIGHT_ANKLE]
    const leftShoulder = landmarks.landmarks[POSE_LANDMARKS.LEFT_SHOULDER]
    const rightShoulder = landmarks.landmarks[POSE_LANDMARKS.RIGHT_SHOULDER]

    const feetDistance = PoseDetector.calculateDistance(leftAnkle, rightAnkle)
    const shoulderWidth = PoseDetector.calculateDistance(leftShoulder, rightShoulder)

    const normalizedDistance = feetDistance / (shoulderWidth + 1e-6)

    let feedback = ''

    if (this.state === 'idle' || this.state === 'down') {
      if (normalizedDistance > 1.5) {
        this.state = 'up'
        feedback = '手臂举高'
      }
    } else if (this.state === 'up') {
      if (normalizedDistance < 0.5) {
        this.state = 'down'
        this.count++
        feedback = `完成第${this.count}个！`
      }
    }

    this.prevFeetDistance = feetDistance

    return {
      count: this.count,
      state: this.state,
      feedback,
      isCorrect: true,
      accuracy: 100
    }
  }

  reset(): void {
    this.count = 0
    this.state = 'idle'
    this.prevFeetDistance = 0
  }
}

export default JumpingJackCounter
