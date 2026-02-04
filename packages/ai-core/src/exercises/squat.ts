/**
 * 运动计数器 - 深蹲
 */
import { PoseLandmarks, PoseDetector, POSE_LANDMARKS } from '../pose/detector'

export interface ExerciseResult {
  count: number
  state: 'idle' | 'up' | 'down'
  feedback: string
  isCorrect: boolean
  accuracy: number
}

export class SquatCounter {
  private count = 0
  private state: 'idle' | 'up' | 'down' = 'idle'
  private correctReps = 0
  private totalReps = 0

  private readonly SQUAT_THRESHOLD = 100
  private readonly STAND_THRESHOLD = 160

  analyze(landmarks: PoseLandmarks): ExerciseResult {
    const leftKnee = PoseDetector.getKneeAngle(landmarks, 'left')
    const rightKnee = PoseDetector.getKneeAngle(landmarks, 'right')
    const avgKnee = (leftKnee + rightKnee) / 2

    let feedback = ''
    let isCorrect = true

    // 状态机
    if (this.state === 'idle' || this.state === 'up') {
      if (avgKnee < this.SQUAT_THRESHOLD) {
        this.state = 'down'
        if (Math.abs(leftKnee - rightKnee) > 20) {
          feedback = '注意保持双腿对称'
          isCorrect = false
        } else {
          feedback = '下蹲到位，保持住'
        }
      }
    } else if (this.state === 'down') {
      if (avgKnee > this.STAND_THRESHOLD) {
        this.state = 'up'
        this.count++
        this.totalReps++
        if (isCorrect) {
          this.correctReps++
        }
        feedback = `完成第${this.count}个！`
      }
    }

    if (!feedback) {
      if (this.state === 'up' && avgKnee > 140) {
        feedback = '准备下蹲'
      } else if (this.state === 'down' && avgKnee > this.SQUAT_THRESHOLD) {
        feedback = '再蹲低一点'
      }
    }

    return {
      count: this.count,
      state: this.state,
      feedback,
      isCorrect,
      accuracy: this.getAccuracy()
    }
  }

  reset(): void {
    this.count = 0
    this.state = 'idle'
    this.correctReps = 0
    this.totalReps = 0
  }

  getAccuracy(): number {
    if (this.totalReps === 0) return 100
    return (this.correctReps / this.totalReps) * 100
  }
}

export default SquatCounter
