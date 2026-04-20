from flask import Flask
from routes.chat import chat_bp
from routes.upload import upload_bp
from services.rag_service import load_data

load_data()

app = Flask(__name__)


app.register_blueprint(chat_bp, url_prefix="/chat")

app.register_blueprint(upload_bp, url_prefix="/upload") 

@app.route("/")


def home():
    return "Finance Advisor Bot Running 🚀"

if __name__ == "__main__":
    app.run(debug=True) 

print(app.url_map)