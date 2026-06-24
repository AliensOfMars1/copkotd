import os

from flask import Flask, render_template

app = Flask(__name__)

# Home route - serves the main homepage
@app.route('/')
def home():
    return render_template('index.html')

# Additional routes can be added later for other pages
# @app.route('/about')
# def about():
#     return render_template('about.html')

if __name__ == '__main__':
    # Railway sets the PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)