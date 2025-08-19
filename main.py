import json
import os

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAI
from flask import Flask, jsonify, request, send_file, send_from_directory

# 🔥 FILL THIS OUT FIRST! 🔥
# Get your Gemini API key by:
# - Selecting "Add Gemini API" in the "Firebase Studio" panel in the sidebar
# - Or by visiting https://g.co/ai/idxGetGeminiKey
os.environ["GOOGLE_API_KEY"] = "TODO"; 
from src.services import search_service

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


if __name__ == "__main__":
    app.run(port=int(os.environ.get('PORT', 80)))
