from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c1ffde52d1a8fd94d22432dfd46b053b38f1f1e79e2bbeba'

@app.route('/')
def index():
    with open('base.html', 'r') as f:
        page = f.read()
    return page


@app.route('/test')
def test():
    return render_template(
        'page_view.html',
        basepath='../',
        pagename='TEST',
        content='FOOBAR'
    )


if __name__ == '__main__':
    app.run(debug=True)
