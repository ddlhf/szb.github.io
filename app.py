import os
import random

from flask import Flask, render_template, jsonify, request  # 补充jsonify导入
from flask_sqlalchemy import SQLAlchemy  # 新增：SQLAlchemy ORM库
from sqlalchemy import func  # 新增：用于SQL函数（如RANDOM()）
import sqlite3
import json

app = Flask(__name__)
# 新增：数据库配置（需与sqlite3路径一致）
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'exams.db')  # 修正路径配置
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭警告
db = SQLAlchemy(app)  # 初始化SQLAlchemy实例

# 新增：定义Question模型类（与数据库表结构对应）
class Question(db.Model):
    __tablename__ = 'exam_questions'  # 添加表名指定
    id = db.Column(db.Integer, primary_key=True)
    question_type = db.Column(db.String(50))
    question_content = db.Column(db.Text)
    options = db.Column(db.JSON)
    correct_answer = db.Column(db.JSON)
    explanation = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_type': self.question_type,
            'question_content': self.question_content,
            'options': self.options,
            'correct_answer': self.correct_answer,
            'explanation': self.explanation
        }

def get_random_questions():
    conn = None
    try:
        conn = sqlite3.connect('exams.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, question_type, question_content, options, correct_answer, explanation '
            'FROM exam_questions ORDER BY RANDOM() LIMIT 5'
        )
        questions = cursor.fetchall()
        result = []
        for q in questions:
            print(f"原始数据库记录: {q}")
            try:
                options = json.loads(q[3]) if q[3] else None
                print(f"解析后的options（题目ID {q[0]}）: {options}")  # 新增调试打印
            except json.JSONDecodeError as e:
                print(f"警告：题目ID {q[0]} 的options字段JSON解析失败，错误：{e}")
                options = None
            result.append({
                '题型': q[1],          # 题型（q[1]）
                '题目内容': q[2],      # 题目内容（q[2]）
                '选项': options,       # 选项（q[3]解析后）
                '正确答案': q[4],      # 正确答案（q[4]）
                '解析': q[5]           # 解析（q[5]）
            })
        print(f"最终题目数据: {result}")
        return result
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        return []
    finally:
        if conn:
            conn.close()

@app.route('/')
def exam_page():
    questions = get_random_questions()
    return render_template('exam.html', questions=questions)

@app.route('/quiz')
def quiz_page():
    questions = get_random_questions()
    print("获取的题目数据：", questions)  # 添加此行，运行后查看控制台输出
    return render_template('quiz.html', questions=questions)

@app.route('/api/random-questions')
def get_random_questions():
    try:
        question_type = request.args.get('type', 'all')
        
        # 严格验证题型参数
        if question_type not in ['single', 'multiple', 'judgement', 'all']:
            return jsonify({"error": "无效的题型参数"}), 400

        # 获取题目逻辑重构
        if question_type == 'all':
            # 确保各题型严格获取5题
            single = Question.query.filter_by(question_type='单项选择题').order_by(func.random()).limit(5).all()
            multiple = Question.query.filter_by(question_type='多项选择题').order_by(func.random()).limit(5).all()
            judgement = Question.query.filter_by(question_type='判断题').order_by(func.random()).limit(5).all()
            
            # 验证数量
            if len(single) !=5 or len(multiple)!=5 or len(judgement)!=5:
                return jsonify({"error": "题库题目数量不足"}), 500
                
            questions = single + multiple + judgement
            random.shuffle(questions)  # 打乱顺序
        else:
            # 映射题型
            type_map = {
                'single': '单项选择题',
                'multiple': '多项选择题',
                'judgement': '判断题'
            }
            questions = Question.query.filter_by(question_type=type_map[question_type])\
                          .order_by(func.random()).limit(5).all()
            if len(questions) !=5:
                return jsonify({"error": "该题型题目数量不足"}), 500

        return jsonify([q.to_dict() for q in questions])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/random-single')
def random_single():
    try:
        # 严格匹配中文题型
        questions = Question.query.filter(
            Question.question_type == '单项选择题'
        ).order_by(func.random()).limit(5).all()
        return jsonify([q.to_dict() for q in questions])
    except Exception as e:
        app.logger.error(f"单选题接口错误: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/random-multiple')
def random_multiple():
    app.logger.info('调用多选题接口')
    try:
        questions = Question.query.filter_by(question_type='多项选择题').order_by(func.random()).limit(5).all()
        return jsonify([q.to_dict() for q in questions])
    except Exception as e:
        app.logger.error(f"多选题接口错误: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/random-judgement')
def random_judgement():
    app.logger.info('调用判断题接口')
    try:
        questions = Question.query.filter_by(question_type='判断题').order_by(func.random()).limit(5).all()
        return jsonify([q.to_dict() for q in questions])
    except Exception as e:
        app.logger.error(f"判断题接口错误: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 首次运行时创建数据库表
    app.run(debug=True)