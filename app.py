from flask import Flask, request, render_template_string
import requests
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


API_KEY = os.environ.get('PUBG_API_KEY')
GROQ_KEY = os.environ.get('GROQ_API_KEY')
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>PUBG 전적 검색</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body class="bg-dark text-white">
        <div class="container mt-5 text-center">
            <h1 class="mb-4">PUBG 전적 검색</h1>
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <form action="/search" method="get">
                        <div class="input-group">
                            <input type="text" name="nickname" class="form-control form-control-lg" placeholder="닉네임 입력">
                            <button type="submit" class="btn btn-warning btn-lg">검색</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''
@app.route('/search')
def search():
    nickname = request.args.get('nickname')

    url = f'https://api.pubg.com/shards/steam/players?filter[playerNames]={nickname}'

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Accept': 'application/vnd.api+json'
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    player_data = data['data'][0]

    player_id = player_data['id']
    player_name = player_data['attributes']['name']
    ban_status = player_data['attributes']['banType']

    

    #Gorq AI 분석 요청

    client = Groq(api_key = GROQ_KEY)
    ai_response = client.chat.completions.create(
        model = 'llama-3.3-70b-versatile',
        messages = [{
            'role':'user',
            'content':f'PUBG 플레이어 {player_name}의 데이터야. 밴 여부: {ban_status}. 이 플레이어에게 한국말로 짧게 조언해줘!'
            }]
    )
    ai_commit = ai_response.choices[0].message.content

    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>{player_name} 전적</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body class="bg-dark text-white">
        <div class="container mt-5">
            <div class="card bg-secondary text-white">
                <div class="card-body text-center">
                    <h1 class="card-title">🎮 {player_name}</h1>
                    <p class="card-text">ID: {player_id}</p>
                    <p class="card-text">밴 여부: {ban_status}</p>
                </div>
            </div>

            <div class="card bg-warning text-dark mt-4">
                <div class="card-body">
                    <h3>🤖 AI 코치 한마디</h3>
                    <p>{ai_commit}</p>
                </div>
            </div>

            <div class="text-center mt-4">
                <a href="/" class="btn btn-outline-light">← 돌아가기</a>
            </div>
        </div>
    </body>
    </html>
    '''





if __name__ == '__main__':
    app.run(debug=True, port=8080)