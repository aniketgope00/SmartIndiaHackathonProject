from flask import Flask, render_template

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/vision-env')
def vision_env():
    # Define YouTube video IDs
    youtube_ids = {
        'camera1': '3qO3sxOtPMc',
        'camera2': 'LiLJd72JLi0',
        'camera3': 'frsF4XjvW0k',
        'camera4': 'HAX3y6femFQ',
        'camera5': 'CZ6NoakNc8s'
    }
    return render_template('vision.html', youtube_ids=youtube_ids)

@app.route('/rl-env')
def rl_env():
    return render_template('rl.html')

if __name__ == "__main__":
    app.run(debug=True)
