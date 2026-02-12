-- 韧翎成长计划种子数据
-- 插入测试用户
INSERT INTO users (phone, password_hash, role, nickname, status) VALUES
('13800138001', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.S6GgrMYRnML4Gy', 'admin', '管理员', 'active'),
('13800138002', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.S6GgrMYRnML4Gy', 'coach', '张教练', 'active'),
('13800138003', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.S6GgrMYRnML4Gy', 'parent', '李家长', 'active');
-- 密码都是: 123456

-- 插入教练
INSERT INTO coaches (user_id, coach_no, name, certification, specialty, hourly_rate, status) VALUES
(2, 'C00000001', '张教练', '["国家一级篮球教练员"]', '["篮球", "体能训练"]', 200.00, 'active');

-- 插入学员
INSERT INTO students (student_no, name, gender, birth_date, height, weight, school, grade, parent_id, coach_id, remaining_lessons, status) VALUES
('S00000001', '小明', '男', '2015-06-15', 135.5, 32.0, '阳光小学', '三年级', 3, 1, 20, 'active'),
('S00000002', '小红', '女', '2016-03-20', 128.0, 26.5, '阳光小学', '二年级', 3, 1, 15, 'active');

-- 插入课程
INSERT INTO courses (name, code, type, category, description, duration, max_students, price, status) VALUES
('篮球基础班', 'BB001', 'group', 'basketball', '适合6-8岁儿童的篮球入门课程', 60, 15, 150.00, 'active'),
('篮球提高班', 'BB002', 'group', 'basketball', '适合有基础的学员提升技能', 90, 12, 200.00, 'active'),
('体能训练课', 'PE001', 'group', 'track_field', '综合体能训练课程', 60, 20, 100.00, 'active'),
('私教一对一', 'PT001', 'private', 'basketball', '一对一专业指导', 60, 1, 300.00, 'active');

-- 插入场地
INSERT INTO venues (name, address, capacity, status) VALUES
('主馆A区', '体育中心1号馆A区', 30, 'active'),
('主馆B区', '体育中心1号馆B区', 30, 'active'),
('室外篮球场', '体育中心室外场地', 50, 'active');
