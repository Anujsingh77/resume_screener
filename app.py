from flask import Flask, render_template, request, jsonify
import os
import json
from utils.pdf_extractor import extract_text_from_pdf
from utils.nlp_processor import extract_skills, compute_tfidf_score
from utils.scorer import score_candidate

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/screen', methods=['POST'])
def screen():
    job_description = request.form.get('job_description', '')
    if not job_description.strip():
        return jsonify({'error': 'Job description is required.'}), 400

    results = []
    files = request.files.getlist('resumes')

    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'Please upload at least one resume PDF.'}), 400

    jd_skills = extract_skills(job_description)

    for file in files:
        if file and file.filename.endswith('.pdf'):
            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(path)
            resume_text = extract_text_from_pdf(path)
            resume_skills = extract_skills(resume_text)
            tfidf_score = compute_tfidf_score(job_description, resume_text)
            candidate_result = score_candidate(
                name=file.filename.replace('.pdf', ''),
                resume_text=resume_text,
                resume_skills=resume_skills,
                jd_skills=jd_skills,
                tfidf_score=tfidf_score
            )
            results.append(candidate_result)
            os.remove(path)  # clean up

    results.sort(key=lambda x: x['score'], reverse=True)
    for i, r in enumerate(results):
        r['rank'] = i + 1

    return jsonify({'candidates': results})


if __name__ == '__main__':
    app.run(debug=True)
