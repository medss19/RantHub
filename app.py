from flask import Flask, render_template, jsonify, request, redirect
from database import load_problems_from_db, load_problem_from_db, add_post_to_db, load_posts_for_problem, upvote_post, load_sorted_posts
import requests

app = Flask(__name__)

@app.route('/')
def home():
    problems = load_problems_from_db()
    return render_template("home.html",
                           problems=problems)
    
@app.route('/terms')
def terms():
    return render_template("terms.html")
    
@app.route('/api/problems')
def list_problems():
    problems = load_problems_from_db()
    return jsonify(problems)
    
@app.route('/problem/<id>')
def problem(id):
    problem = load_problem_from_db(id)
    posts = load_posts_for_problem(id)  # Default sorting by newest
    return render_template("problem.html",
                           problem=problem,
                           posts=posts)
    
@app.route('/api/problem/<id>/posts')
def get_sorted_posts(id):
    sort_method = request.args.get('sort', 'newest')
    posts = load_sorted_posts(id, sort_method)
    return jsonify(posts)
    
@app.route('/problem/<id>/post', methods=['POST'])
def add_post(id):
    # Check if the request is JSON (from AJAX) or form data (from traditional form)
    if request.is_json:
        # Handle JSON request from AJAX
        data = request.get_json()
        content = data.get('content')
        
        if content:
            add_post_to_db(id, content, None)  # No image URL
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": "Content is required"}), 400
    else:
        # Handle traditional form submission
        content = request.form.get('content')
        
        if content:
            add_post_to_db(id, content, None)  # No image URL
        
        return redirect(f'/problem/{id}')

@app.route('/api/post/<post_id>/upvote', methods=['POST'])
def handle_upvote(post_id):
    new_upvote_count = upvote_post(post_id)
    
    if new_upvote_count is not None:
        return jsonify({
            'success': True,
            'upvotes': new_upvote_count
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Post not found'
        }), 404
        
@app.route('/visitor-count')
def visitor_count():
    url = "https://api.countapi.xyz/hit/ranthub.onrender.com/visits"
    try:
        response = requests.get(url)
        return jsonify(response.json())  # Forward the JSON response
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)