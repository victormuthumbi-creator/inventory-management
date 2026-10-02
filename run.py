from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)  # Flask debug mode, http://127.0.0.1:5000
