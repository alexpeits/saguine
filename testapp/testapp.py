from flask import Flask, render_template

app = Flask(__name__, static_folder='web')
app.config['SECRET_KEY'] = 'c1ffde52d1a8fd94d22432dfd46b053b38f1f1e79e2bbeba'

@app.route('/')
def root():
  return app.send_static_file('index.html')

@app.route('/<path:path>')
def static_proxy(path):
  return app.send_static_file(path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
