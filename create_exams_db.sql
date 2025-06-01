-- 创建SQLite数据库表脚本
-- 连接或创建数据库
ATTACH DATABASE 'exams.db' AS exams_db;

-- 创建试题表
-- 创建试题表
CREATE TABLE IF NOT EXISTS exam_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_type TEXT NOT NULL,  -- 题型：单项选择、多项选择、判断、简答
    question_content TEXT NOT NULL,  -- 题目内容
    options TEXT,  -- 选项（JSON格式，如：{"A":"...","B":"..."}
    correct_answer TEXT NOT NULL,  -- 正确答案
    explanation TEXT  -- 解析
);

-- 插入用户提供的试题数据（示例，需根据实际数据补充）
-- 单项选择题示例
INSERT INTO exam_questions (question_type, question_content, options, correct_answer, explanation)
VALUES (
    '单项选择',
    '企业经营决策的核心是（）。',
    '{"A":"筹资决策","B":"投资决策","C":"营运决策","D":"利润分配决策"}',
    'B',
    '企业经营决策的核心在于如何有效配置资源，实现企业的长期发展，这通常通过投资决策来实现。'
);

-- 其他题目按此格式继续插入...