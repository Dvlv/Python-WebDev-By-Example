from web_server import app

app.config.update(
    {
        "TESTING": True,
    }
)

testing_app = app.test_client()
