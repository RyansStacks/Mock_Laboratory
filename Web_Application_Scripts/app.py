from app import app


# run with debugger off for deploy
if __name__ == '__main__':
    app.run(debug=False)