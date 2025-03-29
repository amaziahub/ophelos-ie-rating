def test_is_healthy(app):
    assert app.is_healthy()


def test_greet(app):
    app.greet("e2e_bot", "hi there from greeter bot")
