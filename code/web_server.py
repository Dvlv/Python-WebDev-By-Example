from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = "very secret"


@app.route("/")
def hello_flask():
    products = {"toothpaste": 2.00, "toothbrush": 1.50, "floss": 0.99}
    return render_template("index.html", products=products)


if __name__ == "__main__":
    app.run(debug=True)
