import logging
from app import create_app

# 📝 Logging setup
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s"
)

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False) 