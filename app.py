from flask import Flask, render_template

app = Flask(__name__)



@app.route('/')
def home():
    return render_template('home.html')

@app.route('/vision-env')
def vision_env():
    return render_template('vision.html')

@app.route('/rl-env')
def rl_env():
    return render_template('rl.html')




if __name__ == "__main__":
    app.run(debug= True)