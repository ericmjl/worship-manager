from app import app

if __name__ == "__main__":
    app.secret_key = "super secret key"
    app.config["SESSION_TYPE"] = "filesystem"

    app.run(debug=True, port=8080, host="0.0.0.0")
