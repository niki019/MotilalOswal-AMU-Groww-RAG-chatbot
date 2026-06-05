import os
import json
import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from chatbot import FAQChatbot

app = FastAPI(title="Mutual Fund FAQ Assistant API")

# Initialize Chatbot
chatbot = FAQChatbot()

class ChatRequest(BaseModel):
    message: str

@app.get("/api/status")
async def get_status():
    corpus_path = os.path.join("data", "corpus.json")
    last_updated = "Not available"
    records_count = 0
    
    if os.path.exists(corpus_path):
        try:
            with open(corpus_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                records_count = len(data)
                if records_count > 0:
                    last_updated = data[0].get("last_updated", "Not available")
        except Exception as e:
            print(f"Error reading corpus status: {e}")
            
    return {
        "status": "online",
        "last_updated": last_updated,
        "records_ingested": records_count,
        "api_key_configured": chatbot.api_key is not None
    }

@app.get("/api/schemes")
async def get_schemes():
    try:
        schemes = chatbot.get_schemes()
        return schemes
    except Exception as e:
        print(f"Error retrieving schemes: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    query = request.message.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query message cannot be empty")
        
    try:
        response = chatbot.answer_query(query)
        return response
    except Exception as e:
        print(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Static routes to serve the UI
@app.get("/")
async def serve_index():
    index_path = "index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Mutual Fund FAQ Assistant API is running. index.html not found."}

@app.get("/styles.css")
async def serve_css():
    css_path = "styles.css"
    if os.path.exists(css_path):
        return FileResponse(css_path)
    raise HTTPException(status_code=404, detail="styles.css not found")

@app.get("/app.js")
async def serve_js():
    js_path = "app.js"
    if os.path.exists(js_path):
        return FileResponse(js_path)
    raise HTTPException(status_code=404, detail="app.js not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
