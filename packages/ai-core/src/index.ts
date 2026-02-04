/**
 * AI核心包入口
 */
export { PoseDetector, POSE_LANDMARKS } from './pose/detector'
export type { Point, PoseLandmarks } from './pose/detector'

export { SquatCounter } from './exercises/squat'
export { JumpingJackCounter } from './exercises/jumping-jack'
export type { ExerciseResult } from './exercises/squat'

// 运动计数器工厂
import { SquatCounter } from './exercises/squat'
import { JumpingJackCounter } from './exercises/jumping-jack'

export type ExerciseType = 'squat' | 'jumping_jack' | 'high_knees' | 'pushup' | 'lunge'

export function createExerciseCounter(type: ExerciseType) {
  switch (type) {
    case 'squat':
      return new SquatCounter()
    case 'jumping_jack':
      return new JumpingJackCounter()
    default:
      return new SquatCounter()
  }
}
