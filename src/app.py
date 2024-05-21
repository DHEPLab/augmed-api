from src import create_app, db

app = create_app()


@app.after_request
def commit_after_request(resp, *args, **kwargs):
    db.session.commit()
    return resp


@app.teardown_request
def clean_session(exception=None):
    try:
        db.session.remove()
    finally:
        pass


if __name__ == "__main__":
    app.run()
