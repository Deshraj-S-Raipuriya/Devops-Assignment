import os
from flask import Flask, jsonify

app = Flask(__name__)

# Get environment variables or set default
APP_VERSION = os.getenv('APP_VERSION', '1.0')
APP_TITLE = os.getenv('APP_TITLE', 'Devops for Cloud Assignment')

@app.route('/get_info', methods=['GET'])
def get_info():
    return jsonify({
        "APP_TITLE": APP_TITLE,
        "APP_VERSION": APP_VERSION
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
