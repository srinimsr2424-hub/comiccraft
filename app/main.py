from pathlib import Path
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from google import genai


# Load .env from the project folder
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Read Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

# Create Gemini client
client = genai.Client(api_key=api_key) if api_key else None

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ComicCraft - AI Comic Story Creator</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f4f4f4;
            }

            h1 {
                text-align: center;
                color: #333;
            }

            textarea {
                width: 100%;
                height: 120px;
                padding: 12px;
                font-size: 16px;
                box-sizing: border-box;
            }

            button {
                margin-top: 15px;
                padding: 12px 25px;
                font-size: 16px;
                cursor: pointer;
                background: #333;
                color: white;
                border: none;
                border-radius: 5px;
            }

            button:hover {
                background: #555;
            }

            #result {
                margin-top: 25px;
                padding: 20px;
                background: white;
                border-radius: 8px;
                white-space: pre-wrap;
                line-height: 1.6;
            }
        </style>
    </head>

    <body>
        <h1>🎨 ComicCraft</h1>
        <p style="text-align:center;">
            AI Comic Story Creator using Gemini
        </p>

        <textarea id="idea"
            placeholder="Enter your comic story idea..."></textarea>

        <br>

        <button onclick="generateStory()">✨ Generate Comic Story</button>

        <div id="result">
            Your generated comic story will appear here.
        </div>

        <script>
            async function generateStory() {
                const idea = document.getElementById("idea").value;
                const result = document.getElementById("result");

                if (!idea.trim()) {
                    result.innerText = "Please enter a story idea.";
                    return;
                }

                result.innerText = "⏳ Generating your comic story...";

                const response = await fetch("/generate", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        idea: idea
                    })
                });

                const data = await response.json();

                result.innerText = data.story;
            }
        </script>
    </body>
    </html>
    """


@app.post("/generate")
async def generate(data: dict):
    idea = data.get("idea", "").strip()

    if not idea:
        return {"story": "Please enter a story idea."}

    if client is None:
        return {
            "story": "Gemini API key was not found. Please check your .env file."
        }

    prompt = f"""
Create a short and creative comic story based on this idea:

{idea}

Format the story into exactly 5 comic panels.

For each panel provide:
Panel number
Scene description
Character dialogue

Make it fun, simple, and suitable for a college project demo.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        return {"story": response.text}

    except Exception as e:
        return {
            "story": f"Gemini error: {str(e)}"
        }