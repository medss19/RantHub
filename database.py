from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")

engine = create_engine(DB_URL)

def load_problems_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM problems"))
        problems = []
        for row in result.fetchall():
            problems.append(row._asdict())
        return problems

def load_problem_from_db(id):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM problems WHERE id = :val"),
            {"val": id}
        )
        
        rows = result.fetchall()
        if (len(rows) == 0):
            return None
        return rows[0]._asdict()
    
def add_post_to_db(problem_id, content, image_url=None):
    with engine.connect() as conn:
        query = text("""
                     INSERT INTO posts (problem_id, content, image_url)
                     VALUES (:problem_id, :content, :image_url)
                     """)
        params = {
            "problem_id": problem_id,
            "content": content,
            "image_url": image_url
        }
        conn.execute(query, params)
        conn.commit()
        
def load_posts_for_problem(problem_id):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM posts WHERE problem_id = :problem_id ORDER BY created_at DESC"),
            {"problem_id": problem_id}
        )
        posts = []
        for row in result.fetchall():
            posts.append(row._asdict())
        return posts

def load_sorted_posts(problem_id, sort_method='newest'):
    with engine.connect() as conn:
        if sort_method == 'popular':
            # Sort by upvotes (highest first), then by newest for ties
            query = text("""
                SELECT * FROM posts 
                WHERE problem_id = :problem_id 
                ORDER BY upvotes DESC, created_at DESC
            """)
        else:  # Default to 'newest'
            query = text("""
                SELECT * FROM posts 
                WHERE problem_id = :problem_id 
                ORDER BY created_at DESC
            """)
            
        result = conn.execute(query, {"problem_id": problem_id})
        posts = []
        for row in result.fetchall():
            posts.append(row._asdict())
        return posts

def upvote_post(post_id):
    with engine.connect() as conn:
        # First check if post exists
        check_query = text("SELECT id FROM posts WHERE id = :post_id")
        result = conn.execute(check_query, {"post_id": post_id})
        if result.fetchone() is None:
            return None
            
        # Update the upvotes count
        update_query = text("""
            UPDATE posts
            SET upvotes = upvotes + 1
            WHERE id = :post_id
            RETURNING upvotes
        """)
        
        result = conn.execute(update_query, {"post_id": post_id})
        new_upvote_count = result.fetchone()[0]
        conn.commit()
        
        return new_upvote_count