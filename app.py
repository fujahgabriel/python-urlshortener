from flask import Flask, request, redirect, render_template, url_for
import sqlite3
import hashlib
import base64

app = Flask(__name__)

# Initialize the database
def init_db():
    conn = sqlite3.connect('url_shortener.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls
                 (id INTEGER PRIMARY KEY, original_url TEXT, short_url TEXT)''')
    conn.commit()
    conn.close()

# Initialize the database at the start
init_db()

# Function to generate a short URL
def generate_short_url(original_url):
    hash_object = hashlib.md5(original_url.encode())
    short_hash = base64.urlsafe_b64encode(hash_object.digest()[:6]).decode('utf-8')
    return short_hash

# Route to handle URL shortening
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['original_url']
        short_url = generate_short_url(original_url)
        
        # Save the URL mapping to the database
        conn = sqlite3.connect('url_shortener.db')
        c = conn.cursor()
        c.execute("INSERT INTO urls (original_url, short_url) VALUES (?, ?)", (original_url, short_url))
        conn.commit()
        conn.close()
        
        return render_template('index.html', short_url=short_url)
    return render_template('index.html')

# Route to handle redirection
@app.route('/<short_url>')
def redirect_to_original(short_url):
    conn = sqlite3.connect('url_shortener.db')
    c = conn.cursor()
    c.execute("SELECT original_url FROM urls WHERE short_url = ?", (short_url,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return redirect(result[0])
    else:
        return "URL not found", 404

if __name__ == '__main__':
    app.run(debug=True)
