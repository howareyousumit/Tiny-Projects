"""
Markdown to HTML/PDF Converter Microservice
============================================
A FastAPI-based microservice for converting Markdown files to HTML or PDF.

Installation:
pip install fastapi uvicorn markdown2 weasyprint python-multipart pygments

Run:
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import markdown2
from weasyprint import HTML, CSS
from io import BytesIO
import tempfile
import os
from typing import Optional
from datetime import datetime

app = FastAPI(
    title="Markdown Converter API",
    description="Convert Markdown to HTML or PDF",
    version="1.0.0"
)

# Enable CORS for web clientsuvicorn main:app --host 0.0.0.0 --port 8000 --reload
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# HTML template with professional styling
HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
        }}
        h1 {{ font-size: 2em; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        h2 {{ font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 8px; }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        pre {{
            background-color: #f6f8fa;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
            border: 1px solid #e1e4e8;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        blockquote {{
            border-left: 4px solid #ddd;
            padding-left: 20px;
            margin-left: 0;
            color: #666;
            font-style: italic;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        table th, table td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        table th {{
            background-color: #f2f2f2;
            font-weight: 600;
        }}
        a {{
            color: #0366d6;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
        ul, ol {{
            padding-left: 30px;
        }}
        li {{
            margin: 8px 0;
        }}
        hr {{
            border: none;
            border-top: 2px solid #eee;
            margin: 30px 0;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 0.9em;
            text-align: center;
        }}
    </style>
    </head>
    <body>
        <div class="container">
            {content}
            <div class="footer">
                Generated on {timestamp}
            </div>
        </div>
    </body>
    </html>
    """


class MarkdownConverter:
    """Handle Markdown conversion with advanced features"""
    
    @staticmethod
    def convert_to_html(md_content: str, title: str = "Document") -> str:
        """Convert Markdown to HTML with syntax highlighting and extras"""
        
        # Convert markdown with extras for tables, code blocks, etc.
        html_content = markdown2.markdown(
            md_content,
            extras=[
                "fenced-code-blocks",
                "tables",
                "break-on-newline",
                "code-friendly",
                "cuddled-lists",
                "header-ids",
                "strike",
                "task_list",
                "footnotes",
            ]
        )
        
        # Wrap in template
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_html = HTML_TEMPLATE.format(
            title=title,
            content=html_content,
            timestamp=timestamp
        )
        
        return full_html
    
    @staticmethod
    def convert_to_pdf(html_content: str) -> bytes:
        """Convert HTML to PDF using WeasyPrint"""
        
        # Create PDF from HTML
        pdf_file = BytesIO()
        HTML(string=html_content).write_pdf(pdf_file)
        pdf_file.seek(0)
        
        return pdf_file.getvalue()


@app.get("/", response_class=HTMLResponse)
async def root():
    """API documentation and test interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Markdown Converter API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1000px; margin: 50px auto; padding: 20px; }
            h1 { color: #333; }
            .endpoint { background: #f4f4f4; padding: 15px; margin: 20px 0; border-radius: 5px; }
            code { background: #e0e0e0; padding: 2px 5px; border-radius: 3px; }
            .form-section { margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            textarea { width: 100%; min-height: 200px; padding: 10px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            select { padding: 5px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>Markdown Converter API</h1>
        <p>Convert Markdown files to HTML or PDF format</p>
        
        <div class="endpoint">
            <h3>Endpoints:</h3>
            <p><strong>POST /convert/paste</strong> - Convert pasted Markdown content</p>
            <p><strong>POST /convert/upload</strong> - Convert uploaded Markdown file</p>
            <p><strong>GET /health</strong> - Health check endpoint</p>
            <p><strong>GET /docs</strong> - Interactive API documentation (Swagger UI)</p>
        </div>
        
        <div class="form-section">
            <h3>Test the API - Paste Content</h3>
            <form id="pasteForm">
                <label>Markdown Content:</label><br>
                <textarea id="mdContent" placeholder="# Hello World\n\nPaste your markdown here..."># Sample Document

    ## Introduction
    This is a **sample** markdown document.

    ### Features
    - Bullet points
    - *Italic* and **bold** text
    - `Code snippets`

    ### Code Block
    ```python
    def hello():
        print("Hello, World!")
    ```

    ### Table
    | Name | Age |
    |------|-----|
    | John | 30  |
    | Jane | 25  |
    </textarea><br><br>
                <label>Output Format:</label>
                <select id="outputFormat">
                    <option value="html">HTML</option>
                    <option value="pdf">PDF</option>
                </select><br><br>
                <label>Document Title (optional):</label>
                <input type="text" id="docTitle" placeholder="My Document" style="width: 300px; padding: 5px;"><br><br>
                <button type="submit">Convert</button>
            </form>
        </div>
        
        <div class="form-section">
            <h3>Test the API - Upload File</h3>
            <form id="uploadForm">
                <label>Choose Markdown File:</label><br>
                <input type="file" id="fileInput" accept=".md,.markdown,.txt"><br><br>
                <label>Output Format:</label>
                <select id="uploadFormat">
                    <option value="html">HTML</option>
                    <option value="pdf">PDF</option>
                </select><br><br>
                <button type="submit">Upload & Convert</button>
            </form>
        </div>

        <script>
            document.getElementById('pasteForm').onsubmit = async (e) => {
                e.preventDefault();
                const content = document.getElementById('mdContent').value;
                const format = document.getElementById('outputFormat').value;
                const title = document.getElementById('docTitle').value || 'Document';
                
                const formData = new FormData();
                formData.append('content', content);
                formData.append('output_format', format);
                formData.append('title', title);
                
                try {
                    const response = await fetch('/convert/paste', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `document.${format}`;
                        a.click();
                    } else {
                        alert('Conversion failed!');
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            };
            
            document.getElementById('uploadForm').onsubmit = async (e) => {
                e.preventDefault();
                const file = document.getElementById('fileInput').files[0];
                const format = document.getElementById('uploadFormat').value;
                
                if (!file) {
                    alert('Please select a file!');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', file);
                formData.append('output_format', format);
                
                try {
                    const response = await fetch('/convert/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `converted.${format}`;
                        a.click();
                    } else {
                        alert('Conversion failed!');
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            };
        </script>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Markdown Converter API"
    }


@app.post("/convert/paste")
async def convert_paste(
    content: str = Form(..., description="Markdown content to convert"),
    output_format: str = Form(..., description="Output format: 'html' or 'pdf'"),
    title: Optional[str] = Form("Document", description="Document title")
    ):
    """
    Convert pasted Markdown content to HTML or PDF
    
    - **content**: Raw markdown text
    - **output_format**: 'html' or 'pdf'
    - **title**: Optional document title
    """
    
    if not content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    
    if output_format not in ["html", "pdf"]:
        raise HTTPException(status_code=400, detail="output_format must be 'html' or 'pdf'")
    
    try:
        converter = MarkdownConverter()
        
        # Convert to HTML first
        html_content = converter.convert_to_html(content, title)
        
        if output_format == "html":
            return StreamingResponse(
                BytesIO(html_content.encode('utf-8')),
                media_type="text/html",
                headers={
                    "Content-Disposition": f"attachment; filename={title.replace(' ', '_')}.html"
                }
            )
        else:  # PDF
            pdf_content = converter.convert_to_pdf(html_content)
            return StreamingResponse(
                BytesIO(pdf_content),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={title.replace(' ', '_')}.pdf"
                }
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")


@app.post("/convert/upload")
async def convert_upload(
    file: UploadFile = File(..., description="Markdown file to convert"),
    output_format: str = Form(..., description="Output format: 'html' or 'pdf'")
    ):
    """
    Convert uploaded Markdown file to HTML or PDF
    
    - **file**: Markdown file (.md, .markdown, .txt)
    - **output_format**: 'html' or 'pdf'
    """
    
    # Validate file extension
    allowed_extensions = [".md", ".markdown", ".txt"]
    file_ext = os.path.splitext(file.filename)[0] if file.filename else ""
    
    if output_format not in ["html", "pdf"]:
        raise HTTPException(status_code=400, detail="output_format must be 'html' or 'pdf'")
    
    try:
        # Read file content
        content = await file.read()
        md_content = content.decode('utf-8')
        
        if not md_content.strip():
            raise HTTPException(status_code=400, detail="File is empty")
        
        converter = MarkdownConverter()
        
        # Use filename (without extension) as title
        title = os.path.splitext(file.filename)[0] if file.filename else "Document"
        
        # Convert to HTML
        html_content = converter.convert_to_html(md_content, title)
        
        if output_format == "html":
            return StreamingResponse(
                BytesIO(html_content.encode('utf-8')),
                media_type="text/html",
                headers={
                    "Content-Disposition": f"attachment; filename={title.replace(' ', '_')}.html"
                }
            )
        else:  # PDF
            pdf_content = converter.convert_to_pdf(html_content)
            return StreamingResponse(
                BytesIO(pdf_content),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={title.replace(' ', '_')}.pdf"
                }
            )
    
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be a valid text file with UTF-8 encoding")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)