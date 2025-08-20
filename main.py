import json
import os

from langchain_core.messages import HumanMessage
import hashlib
import sqlite3
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAI
from flask import Flask, jsonify, request, send_file, send_from_directory

# 🔥 FILL THIS OUT FIRST! 🔥\n# Get your Gemini API key by:
# Get your Gemini API key by:
# - Selecting "Add Gemini API" in the "Firebase Studio" panel in the sidebar
# - Or by visiting https://g.co/ai/idxGetGeminiKey
os.environ["GOOGLE_API_KEY"] = "TODO"; 
from src.services import search_service


def create_context_db(db_path="Context.db"):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                setting_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                setting_key TEXT,
                setting_value TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME,
                summary TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS context_points (
                point_id INTEGER PRIMARY KEY,
                session_id INTEGER,
                type TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                related_elements TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_elements (
                element_id INTEGER PRIMARY KEY,
                project_path TEXT,
                type TEXT,
                summary TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                relationship_id INTEGER PRIMARY KEY,
                from_id INTEGER,
                to_id INTEGER,
                type TEXT
                -- FOREIGN KEY constraints could be added here depending on complexity
            )
        ')')

        conn.commit()
        print(f"Context.db created or updated at {db_path}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

app = Flask(__name__)


@app.route("/")
def index():
    return send_file('web/index.html')


@app.route("/api/generate", methods=["POST"])
def generate_api():
    if request.method == "POST":
        if os.environ["GOOGLE_API_KEY"] == 'TODO':
            return jsonify({ "error": '''
                To get started, get an API key at
                https://g.co/ai/idxGetGeminiKey and enter it in
                main.py
                '''.replace('\n', '') })
        try:
            req_body = request.get_json()
            content = req_body.get("contents")
            model = ChatGoogleGenerativeAI(model=req_body.get("model"))
            message = HumanMessage(
                content=content
            )
            response = model.stream([message])
            def stream():
                for chunk in response:
                    yield 'data: %s\n\n' % json.dumps({ "text": chunk.content })

            return stream(), {'Content-Type': 'text/event-stream'}

        except Exception as e:
            return jsonify({ "error": str(e) })

# Flask route for Yahoo search
@app.route("/search/yahoo", methods=["GET"])
def search_yahoo_api():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Query parameter is missing"}), 400
    
    results = search_service.search_yahoo(query)
    if results is None:
        return jsonify({"error": "Failed to perform Yahoo search"}), 500
    
    return jsonify(results)

# Flask route for Bing search
@app.route("/search/bing", methods=["GET"])
def search_bing_api():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Query parameter is missing"}), 400
    
    results = search_service.search_bing(query)
    if results is None:
        return jsonify({"error": "Failed to perform Bing search"}), 500
    
    return jsonify(results)

# Function to search for latest AI generator features and improvements
def search_latest_ai_features(query):
    # Use both search services to gather information
    yahoo_results = search_service.search_yahoo(f"latest AI image video generator features {query} 1K 4K 8K")
    bing_results = search_service.search_bing(f"new AI multimedia generation improvements {query} high resolution")
    
    # Combine or process results as needed. This is a simple combination example.
    combined_results = {
        "yahoo": yahoo_results,
        "bing": bing_results
    }
    return combined_results

def get_db_connection(db_path):
    """Gets a database connection."""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row # Optional: allows accessing columns by name
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def get_user_id():
    """Placeholder to get the current user ID."""
    # TODO: Implement actual user authentication and retrieval
    # For now, return a placeholder or default user ID
    return 1 # Assuming a default user with ID 1

# Helper function to ensure the uploads directory exists
def ensure_uploads_dir():
    upload_folder = os.path.abspath('uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    return upload_folder

# Call database creation functions on startup (or when needed)
create_context_db(os.path.abspath("Context.db"))
# create_knowler_db(os.path.abspath("Knowler.db")) # Call when needed
@app.route("/api/save-to-drive", methods=["POST"])
def save_to_drive_api():
    if request.method == "POST":
        req_body = request.get_json()
        content = req_body.get("content")
        access_token = req_body.get("accessToken")

        if not content or not access_token:
            return jsonify({"error": "Missing content or accessToken"}), 400

        print(f"Content: {content}")
        print(f"Access Token: {access_token}")
    
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('web', path)

@app.route("/api/upload", methods=["POST"])
def upload_api():
    if request.method == "POST":
        upload_folder = ensure_uploads_dir()
        uploaded_files = request.files
        uploaded_file_info = []
        if not uploaded_files:
            return jsonify({"error": "No files uploaded"}), 400

        conn = None
        try:
            conn = get_db_connection(os.path.abspath("Context.db"))
            if conn is None:
                return jsonify({"error": "Failed to connect to database"}), 500
            
            user_id = get_user_id() # Get the placeholder user ID

            for name, file in uploaded_files.items():
                filename = file.filename
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                
                # Extract basic metadata
                filesize = os.path.getsize(filepath)
                content_type = file.content_type
                
                # Generate metadata hash (simple hash of basic metadata string)
                metadata_string = f"{filename}-{filesize}-{content_type}" # Consider adding more metadata here
                metadata_hash = hashlib.sha256(metadata_string.encode()).hexdigest()
                
                # Insert into uploaded_files table
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO uploaded_files (user_id, original_name, saved_path, mime_type, size, metadata_hash)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, filename, filepath, content_type, filesize, metadata_hash))
                conn.commit()
                
                uploaded_file_info.append({"filename": filename, "metadata_hash": metadata_hash, "saved_path": filepath})
                
                print(f"Saved file: {filename} to {filepath}, Metadata Hash: {metadata_hash}, Stored in DB")

            return jsonify({
                "message": "Files uploaded successfully",
                "uploaded_files": uploaded_file_info
            }), 200

        except sqlite3.Error as e:
            if conn:
                conn.rollback() # Rollback changes if an error occurs
            return jsonify({"error": f"Database error during file upload: {e}"}), 500
        except Exception as e:
            return jsonify({"error": f"An error occurred during file upload: {e}"}), 500
        finally:
            if conn:
                conn.close()


def create_context_db(db_path=os.path.abspath("Context.db")):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                setting_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                setting_key TEXT,
                setting_value TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME,
                summary TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS context_points (
                point_id INTEGER PRIMARY KEY,
                session_id INTEGER,
                type TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                related_elements TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_elements (
                element_id INTEGER PRIMARY KEY,
                project_path TEXT,
                type TEXT,
                summary TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                relationship_id INTEGER PRIMARY KEY,
                from_id INTEGER,
                to_id INTEGER,
                type TEXT
                -- FOREIGN KEY constraints could be added here depending on complexity
            )
        ''')

        # Add the new uploaded_files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS uploaded_files (
                file_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                original_name TEXT,
                saved_path TEXT,
                mime_type TEXT,
                size INTEGER,
                metadata_hash TEXT,
                upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        conn.commit()
        print(f"Context.db created or updated at {db_path}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def create_knowler_db(db_path=os.path.abspath("Knowler.db")):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS algorithms (
                algo_id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT,
                complexity TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_patterns (
                pattern_id INTEGER PRIMARY KEY,
                name TEXT,
                language TEXT,
                description TEXT,
                example_code TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS syntax_rules (
                rule_id INTEGER PRIMARY KEY,
                language TEXT,
                rule_description TEXT,
                example TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS language_info (
                lang_id INTEGER PRIMARY KEY,
                name TEXT,
                version TEXT,
                description TEXT
            )
        ''')

        conn.commit()
        print(f"Knowler.db created or updated at {db_path}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Ensure databases are created when the app starts
    create_context_db(os.path.abspath("Context.db"))
    # create_knowler_db(os.path.abspath("Knowler.db")) # Uncomment if you need to create Knowler.db on startup
    app.run(port=int(os.environ.get('PORT', 80)))


