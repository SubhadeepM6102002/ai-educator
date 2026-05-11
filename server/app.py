from db import get_db_connection
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)


@app.route('/signup', methods=['POST'])
def signup():

    try:

        data = request.json

        name = data.get('name')
        password = data.get('password')

        if not name or not password:
            return jsonify({
                "message": "Missing fields"
            }), 400

        conn = get_db_connection()

        existing_user = conn.execute(
            'SELECT * FROM users WHERE name = ?',
            (name,)
        ).fetchone()

        if existing_user:

            conn.close()

            return jsonify({
                "message": "User already exists"
            }), 400

        conn.execute(
            'INSERT INTO users (name, password) VALUES (?, ?)',
            (name, password)
        )

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Signup successful"
        })

    except Exception as e:

        return jsonify({
            "message": str(e)
        }), 500

@app.route('/login', methods=['POST'])
def login():

    try:

        data = request.json

        name = data.get('name')
        password = data.get('password')

        conn = get_db_connection()

        user = conn.execute(
            'SELECT * FROM users WHERE name = ? AND password = ?',
            (name, password)
        ).fetchone()

        conn.close()

        if user:

            return jsonify({
                "message": "Login successful"
            })

        return jsonify({
            "message": "Invalid username or password"
        }), 401

    except Exception as e:

        return jsonify({
            "message": str(e)
        }), 500
     
# ============================================
# ADD SAVE PROGRESS ROUTE HERE
# ============================================
@app.route('/save_progress', methods=['POST'])
def save_progress():

    try:

        data = request.json

        username = data.get('username')
        playlist = data.get('playlist')
        completedVideos = json.dumps(data.get('completedVideos', []))
        feedbackState = json.dumps(data.get('feedbackState', {}))
        streak = data.get('streak', 0)
        progressPercent = data.get('progressPercent', 0)

        conn = get_db_connection()

        existing = conn.execute(
            'SELECT * FROM progress WHERE username = ?',
            (username,)
        ).fetchone()

        if existing:

            conn.execute('''
                UPDATE progress
                SET playlist = ?,
                    completedVideos = ?,
                    feedbackState = ?,
                    streak = ?,
                    progressPercent = ?
                WHERE username = ?
            ''', (
                playlist,
                completedVideos,
                feedbackState,
                streak,
                progressPercent,
                username
            ))

        else:

            conn.execute('''
                INSERT INTO progress (
                    username,
                    playlist,
                    completedVideos,
                    feedbackState,
                    streak,
                    progressPercent
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                username,
                playlist,
                completedVideos,
                feedbackState,
                streak,
                progressPercent
            ))

        conn.commit()
        conn.close()

        return jsonify({
            'message': 'Progress saved successfully'
        })

    except Exception as e:

        return jsonify({
            'message': str(e)
        }), 500

   # ============================================
# ADD SAVE LOAD ROUTE HERE
# ============================================
@app.route('/load_progress/<username>', methods=['GET'])
def load_progress(username):

    try:

        conn = get_db_connection()

        progress = conn.execute(
            'SELECT * FROM progress WHERE username = ?',
            (username,)
        ).fetchone()

        conn.close()

        if not progress:

            return jsonify({
                'message': 'No progress found'
            })

        return jsonify({
            'playlist': progress['playlist'],
            'completedVideos': json.loads(progress['completedVideos']),
            'feedbackState': json.loads(progress['feedbackState']),
            'streak': progress['streak'],
            'progressPercent': progress['progressPercent']
        })

    except Exception as e:

        return jsonify({
            'message': str(e)
        }), 500
# ========== PERFORMANCE PREDICTION (RULE-BASED) ==========


@app.route('/predict_performance', methods=['POST'])
def predict_performance():
    """
    features = [
        progress,            # 0: % completed
        prep_hours,          # 1: recent study hours (can be decimal)
        streak_length,       # 2: current streak (days)
        lectures_completed,  # 3: total completed lectures
        uc_ratio             # 4: understood_to_confused_ratio
    ]
    """
    try:
        data = request.json
        features = data.get('features')

        if not features or len(features) != 5:
            return jsonify({
                "prediction": "Error: Please provide 5 features."
            }), 400

        progress, prep_hours, streak_len, lectures_completed, uc_ratio = features

        # 1. Very low progress + some confusion -> At Risk
        #    (If progress < 30 but everything is understood, don't punish.)
        if progress < 30 and uc_ratio < 1.0:
            result = "At Risk"

        # 2. High confusion relative to understanding -> At Risk
        elif uc_ratio < 0.5:
            result = "At Risk"

        # 3. Medium progress but very low effort -> At Risk
        elif 30 <= progress < 60 and prep_hours < 1.5:
            result = "At Risk"

        # 4. Good overall profile -> On Track
        elif progress >= 60 and streak_len >= 3 and uc_ratio >= 1.0:
            result = "On Track"

        # 5. Default: On Track (borderline)
        else:
            result = "On Track"

        return jsonify({"prediction": result})

    except Exception as e:
        return jsonify({"prediction": "Error: " + str(e)}), 400


# ========== SIMPLE RECOMMENDATION ENDPOINT ==========

@app.route('/recommend', methods=['POST'])
def recommend():
    """
    Receives:
      {
        "confused_indices": [0, 2],
        "lecture_titles": ["Graph 1", "Sliding Window", ...]
      }

    Returns readable titles instead of generic IDs.
    """
    try:
        data = request.json
        confused_indices = data.get('confused_indices', [])
        lecture_titles = data.get('lecture_titles', [])

        if not confused_indices:
            return jsonify({"recommendations": ["Revise fundamentals", "Practice more problems"]})

        recs = []
        for idx in confused_indices:
            if 0 <= idx < len(lecture_titles):
                recs.append(lecture_titles[idx])
            neighbor = idx + 1
            if neighbor < len(lecture_titles):
                recs.append(lecture_titles[neighbor])

        # deduplicate and keep first few
        seen = set()
        final = []
        for title in recs:
            if title not in seen:
                seen.add(title)
                final.append(title)
            if len(final) >= 4:
                break

        if not final:
            final = ["Revise key concepts", "Do more practice problems"]

        return jsonify({"recommendations": final})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
