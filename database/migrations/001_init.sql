-- 易乐航数据库初始化脚本
-- 创建数据库
CREATE DATABASE IF NOT EXISTS yilehang;

-- 使用数据库
\c yilehang;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255),
    role VARCHAR(20) DEFAULT 'parent',
    wechat_openid VARCHAR(100) UNIQUE,
    avatar VARCHAR(500),
    nickname VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 教练表
CREATE TABLE IF NOT EXISTS coaches (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) UNIQUE,
    coach_no VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    certification TEXT,
    specialty TEXT,
    hourly_rate DECIMAL(10, 2),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 学员表
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    student_no VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    gender VARCHAR(10),
    birth_date DATE,
    height DECIMAL(5, 2),
    weight DECIMAL(5, 2),
    school VARCHAR(100),
    grade VARCHAR(20),
    parent_id INTEGER REFERENCES users(id),
    coach_id INTEGER REFERENCES coaches(id),
    remaining_lessons INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 家长-学员关联表
CREATE TABLE IF NOT EXISTS parent_student_relations (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER REFERENCES users(id),
    student_id INTEGER REFERENCES students(id),
    relation VARCHAR(20),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 课程表
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    type VARCHAR(20) DEFAULT 'group',
    category VARCHAR(50),
    description TEXT,
    duration INTEGER DEFAULT 60,
    max_students INTEGER DEFAULT 20,
    price DECIMAL(10, 2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 场地表
CREATE TABLE IF NOT EXISTS venues (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    capacity INTEGER DEFAULT 50,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 排课表
CREATE TABLE IF NOT EXISTS schedules (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses(id),
    coach_id INTEGER REFERENCES coaches(id),
    venue_id INTEGER REFERENCES venues(id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    capacity INTEGER DEFAULT 20,
    enrolled_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 考勤表
CREATE TABLE IF NOT EXISTS attendances (
    id SERIAL PRIMARY KEY,
    schedule_id INTEGER REFERENCES schedules(id),
    student_id INTEGER REFERENCES students(id),
    check_in_time TIMESTAMP,
    check_in_method VARCHAR(20),
    status VARCHAR(20) DEFAULT 'enrolled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 体测记录表
CREATE TABLE IF NOT EXISTS fitness_tests (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    test_date DATE NOT NULL,
    tester_id INTEGER REFERENCES coaches(id),
    height DECIMAL(5, 2),
    weight DECIMAL(5, 2),
    bmi DECIMAL(4, 2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 体测指标表
CREATE TABLE IF NOT EXISTS fitness_metrics (
    id SERIAL PRIMARY KEY,
    test_id INTEGER REFERENCES fitness_tests(id),
    metric_type VARCHAR(20) NOT NULL,
    metric_name VARCHAR(50) NOT NULL,
    value DECIMAL(10, 2) NOT NULL,
    score DECIMAL(5, 2),
    national_percentile DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI训练记录表
CREATE TABLE IF NOT EXISTS training_sessions (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    exercise_type VARCHAR(50) NOT NULL,
    duration INTEGER NOT NULL,
    reps_count INTEGER DEFAULT 0,
    accuracy_score DECIMAL(5, 2),
    calories_burned DECIMAL(6, 2),
    video_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 作业模板表
CREATE TABLE IF NOT EXISTS homework_templates (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    exercise_type VARCHAR(50) NOT NULL,
    target_reps INTEGER NOT NULL,
    points INTEGER DEFAULT 10,
    difficulty VARCHAR(20) DEFAULT 'normal',
    video_demo_url VARCHAR(500),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 作业分配表
CREATE TABLE IF NOT EXISTS homework_assignments (
    id SERIAL PRIMARY KEY,
    template_id INTEGER REFERENCES homework_templates(id),
    student_id INTEGER REFERENCES students(id),
    coach_id INTEGER REFERENCES coaches(id),
    due_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 作业提交表
CREATE TABLE IF NOT EXISTS homework_submissions (
    id SERIAL PRIMARY KEY,
    assignment_id INTEGER REFERENCES homework_assignments(id) UNIQUE,
    video_url VARCHAR(500) NOT NULL,
    reps_completed INTEGER DEFAULT 0,
    ai_score DECIMAL(5, 2),
    coach_score DECIMAL(5, 2),
    feedback TEXT,
    points_earned INTEGER DEFAULT 0,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    graded_at TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_students_parent_id ON students(parent_id);
CREATE INDEX idx_students_coach_id ON students(coach_id);
CREATE INDEX idx_schedules_start_time ON schedules(start_time);
CREATE INDEX idx_schedules_coach_id ON schedules(coach_id);
CREATE INDEX idx_fitness_tests_student_id ON fitness_tests(student_id);
CREATE INDEX idx_training_sessions_student_id ON training_sessions(student_id);
CREATE INDEX idx_homework_assignments_student_id ON homework_assignments(student_id);
