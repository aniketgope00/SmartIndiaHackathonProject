from flask import Flask, render_template
import pandas as pd

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/vision-env')
def vision_env():

    data = pd.read_csv("object_detection_data.csv")
    data = data.values.tolist()

    # Define YouTube video IDs
    youtube_ids = {
        'camera1': '3qO3sxOtPMc',
        'camera2': 'LiLJd72JLi0',
        'camera3': 'frsF4XjvW0k',
        'camera4': 'HAX3y6femFQ',
        'camera5': 'CZ6NoakNc8s'
    }
    return render_template('vision.html', youtube_ids=youtube_ids, data = data)

@app.route('/rl-env')
def rl_env():
    return render_template('rl.html')

@app.route("/aboutus")
def about_us():
    return render_template('aboutus.html')

if __name__ == "__main__":
    app.run(debug=True)
