from flask import Flask, render_template, request, jsonify
import json
from difflib import get_close_matches

app = Flask(__name__,template_folder='templates')

# โหลดฐานข้อมูล
def load_knowledge_base():
    with open('knowledge_base.json', 'r') as file:
        return json.load(file)

# บันทึกฐานข้อมูล
def save_knowledge_base(data):
    with open('knowledge_base.json', 'w') as file:
        json.dump(data, file, indent=2)

# ค้นหาคำถามที่คล้ายที่สุด
def find_best_match(user_question, questions):
    matches = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

# ดึงคำตอบจากฐานข้อมูล
def get_answer_for_question(question, knowledge_base):
    for q in knowledge_base["question"]:
        if q["question"] == question:
            return q["answer"]
    return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message')

    knowledge_base = load_knowledge_base()
    best_match = find_best_match(user_input, [q["question"] for q in knowledge_base["question"]])

    if best_match:
        response = get_answer_for_question(best_match, knowledge_base)
    else:
        response = "ผมไม่รู้คำตอบ คุณช่วยสอนผมได้ไหม?"

    return jsonify({'response': response, 'question': user_input, 'needs_learning': best_match is None})

@app.route('/teach', methods=['POST'])
def teach():
    data = request.get_json()
    new_question = data.get('question')
    new_answer = data.get('answer')

    if not new_question or not new_answer:
        return jsonify({'status': 'error', 'message': 'ใส่คำผิด'})

    knowledge_base = load_knowledge_base()
    knowledge_base["question"].append({"question": new_question, "answer": new_answer})
    save_knowledge_base(knowledge_base)

    return jsonify({'status': 'success', 'message': 'ขอบคุณครับที่สอนคำใหม่ให้กับผม.'})

if __name__ == '__main__':
    app.run(debug=True)