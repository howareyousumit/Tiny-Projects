from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
from typing import Optional

app = FastAPI(title="JSON Formatter & Validator")

class JSONInput(BaseModel):
    text: str
    indent: Optional[int] = 4

class JSONResponse(BaseModel):
    success: bool
    formatted: Optional[str] = None
    error: Optional[str] = None
    error_line: Optional[int] = None
    error_column: Optional[int] = None

@app.post("/api/format", response_model=JSONResponse)
async def format_json(data: JSONInput):
    """
    Format and validate JSON text.
    - Converts single quotes to double quotes
    - Validates JSON structure
    - Returns formatted JSON or error details
    """
    try:
        # Replace single quotes with double quotes
        text = data.text.replace("'", '"')
        
        # Try to parse the JSON
        parsed = json.loads(text)
        
        # Format with specified indent
        formatted = json.dumps(parsed, indent=data.indent, ensure_ascii=False)
        
        return JSONResponse(
            success=True,
            formatted=formatted
        )
    
    except json.JSONDecodeError as e:
        # Extract error details
        return JSONResponse(
            success=False,
            error=f"JSON Error: {e.msg}",
            error_line=e.lineno,
            error_column=e.colno
        )
    
    except Exception as e:
        return JSONResponse(
            success=False,
            error=f"Error: {str(e)}"
        )

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the HTML interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JSON Formatter & Validator</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .header p {
                font-size: 1.1em;
                opacity: 0.9;
            }
            
            .content {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                padding: 30px;
            }
            
            .panel {
                display: flex;
                flex-direction: column;
            }
            
            .panel h2 {
                color: #333;
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            
            textarea {
                width: 100%;
                height: 500px;
                padding: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                resize: vertical;
                transition: border-color 0.3s;
            }
            
            textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            
            .controls {
                display: flex;
                gap: 15px;
                margin-top: 15px;
                flex-wrap: wrap;
            }
            
            .indent-control {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .indent-control label {
                font-weight: 500;
                color: #555;
            }
            
            .indent-control input {
                width: 60px;
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
            }
            
            button {
                padding: 12px 30px;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            
            .btn-secondary {
                background: #f0f0f0;
                color: #333;
            }
            
            .btn-secondary:hover {
                background: #e0e0e0;
            }
            
            .error-message {
                background: #fee;
                border-left: 4px solid #f44336;
                padding: 15px;
                margin-top: 15px;
                border-radius: 6px;
                color: #c62828;
                display: none;
            }
            
            .error-message.show {
                display: block;
            }
            
            .success-message {
                background: #e8f5e9;
                border-left: 4px solid #4caf50;
                padding: 15px;
                margin-top: 15px;
                border-radius: 6px;
                color: #2e7d32;
                display: none;
            }
            
            .success-message.show {
                display: block;
            }
            
            .loading {
                opacity: 0.6;
                pointer-events: none;
            }
            
            @media (max-width: 768px) {
                .content {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔧 JSON Formatter & Validator</h1>
                <p>Format, validate, and beautify your JSON data</p>
            </div>
            
            <div class="content">
                <div class="panel">
                    <h2>Input JSON</h2>
                    <textarea id="input" placeholder="Paste your JSON here...&#10;&#10;Example:&#10;{'name': 'John', 'age': 30, 'city': 'New York'}"></textarea>
                    
                    <div class="controls">
                        <div class="indent-control">
                            <label for="indent">Indent Spaces:</label>
                            <input type="number" id="indent" value="4" min="1" max="8">
                        </div>
                        <button class="btn-primary" onclick="formatJSON()">Format & Validate</button>
                        <button class="btn-secondary" onclick="clearAll()">Clear All</button>
                        <button class="btn-secondary" onclick="copyOutput()">Copy Output</button>
                    </div>
                    
                    <div class="error-message" id="error"></div>
                    <div class="success-message" id="success"></div>
                </div>
                
                <div class="panel">
                    <h2>Formatted JSON</h2>
                    <textarea id="output" readonly placeholder="Formatted JSON will appear here..."></textarea>
                </div>
            </div>
        </div>
        
        <script>
            async function formatJSON() {
                const input = document.getElementById('input').value;
                const indent = parseInt(document.getElementById('indent').value);
                const outputElem = document.getElementById('output');
                const errorElem = document.getElementById('error');
                const successElem = document.getElementById('success');
                
                // Clear previous messages
                errorElem.classList.remove('show');
                successElem.classList.remove('show');
                outputElem.value = '';
                
                if (!input.trim()) {
                    showError('Please enter some JSON text');
                    return;
                }
                
                try {
                    document.body.classList.add('loading');
                    
                    const response = await fetch('/api/format', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            text: input,
                            indent: indent
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        outputElem.value = data.formatted;
                        showSuccess('✓ JSON is valid and formatted successfully!');
                    } else {
                        let errorMsg = data.error;
                        if (data.error_line) {
                            errorMsg += ` (Line: ${data.error_line}, Column: ${data.error_column})`;
                        }
                        showError(errorMsg);
                    }
                } catch (error) {
                    showError('Network error: ' + error.message);
                } finally {
                    document.body.classList.remove('loading');
                }
            }
            
            function clearAll() {
                document.getElementById('input').value = '';
                document.getElementById('output').value = '';
                document.getElementById('error').classList.remove('show');
                document.getElementById('success').classList.remove('show');
            }
            
            function copyOutput() {
                const output = document.getElementById('output');
                if (!output.value) {
                    showError('Nothing to copy! Format JSON first.');
                    return;
                }
                
                output.select();
                document.execCommand('copy');
                showSuccess('✓ Copied to clipboard!');
            }
            
            function showError(message) {
                const errorElem = document.getElementById('error');
                errorElem.textContent = message;
                errorElem.classList.add('show');
            }
            
            function showSuccess(message) {
                const successElem = document.getElementById('success');
                successElem.textContent = message;
                successElem.classList.add('show');
            }
            
            // Keyboard shortcut: Ctrl/Cmd + Enter to format
            document.getElementById('input').addEventListener('keydown', function(e) {
                if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                    e.preventDefault();
                    formatJSON();
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)