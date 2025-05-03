import os
from flask import Flask, render_template, request, redirect, url_for, flash
from anthropic import Anthropic
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

def generate_autobiography(life_events):
    """Generate autobiography using Claude API."""
    client = Anthropic(api_key=app.config['ANTHROPIC_API_KEY'])

    prompt = f"""You are an autobiographer helping someone write the story of their life. 
Use the provided life events to extract key moments, emotional themes, and turning points. 
Then, generate an autobiography with a title, themes, chapter outline, and a sample chapter.

LIFE EVENTS:
{life_events}

OUTPUT:
1. Title
2. Life Themes (3-5 key themes)
3. Chapter Outline (5-7 chapters with brief descriptions)
4. Sample Chapter 1 (500-800 words, narrative-style)
"""

    try:
        message = client.messages.create(
            model="claude-3-opus-20240229",  # Or use claude-3-sonnet for cheaper option
            max_tokens=2000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        return ''.join(block.text for block in message.content if hasattr(block, "text"))

    except Exception as e:
        return f"Error generating autobiography: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        life_events = request.form.get('life_events', '')
        if not life_events:
            flash('Please provide some information about your life.')
            return redirect(url_for('index'))

        result = generate_autobiography(life_events)

        # Basic parsing logic
        sections = result.split('\n')
        title, themes, chapters, sample_chapter = "Your Autobiography", [], [], ""
        current = None

        for line in sections:
            line = line.strip()
            if not line: continue

            if "Title" in line:
                current = "title"
                continue
            elif "Life Themes" in line:
                current = "themes"
                continue
            elif "Chapter Outline" in line:
                current = "chapters"
                continue
            elif "Sample Chapter" in line:
                current = "sample"
                continue

            if current == "title":
                title = line
            elif current == "themes":
                themes.append(line)
            elif current == "chapters":
                chapters.append(line)
            elif current == "sample":
                sample_chapter += line + "\n"

        return render_template('result.html', title=title, themes=themes, chapters=chapters, sample_chapter=sample_chapter)

    return render_template('index.html')
    
if __name__ == '__main__':
    app.run(debug=True, port=5001)

