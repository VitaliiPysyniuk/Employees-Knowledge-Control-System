from fastapi import Request, HTTPException, status
from aiohttp import ClientSession
from six.moves.urllib.request import urlopen
import json
from jose import jwt
from typing import List
from datetime import datetime
from itertools import groupby
from time import time
import shutil
import os


from core.congif import settings
from schemas.user import UserSignIn, UserSignUp
from schemas.question import FullQuestion, QuestionWithAnswersForAdmin
from schemas.quiz import UserAnswer



def get_session(request: Request) -> ClientSession:
    return request.app.state.session


def parse_questions(instances):
    questions = [FullQuestion(**instance).dict() for instance in instances]
    grouped_questions = groupby(questions, key=lambda item: item['id'])
    parsed_questions = list()

    for key, value in grouped_questions:
        question = {
            'id': key,
            'question_text': '',
            'categories': dict(),
            'answers': dict()
        }

        for item in value:
            question['question_text'] = item['question_text']
            if item['id_1'] and item['id_1'] not in question['answers']:
                question['answers'][item['id_1']] = {
                    'id': item['id_1'],
                    'answer_text': item['answer_text'],
                    'is_correct': item['is_correct']
                }
            if item['id_2'] and item['id_2'] not in question['categories']:
                question['categories'][item['id_2']] = {
                    'id': item['id_2'],
                    'name': item['name'],
                    'description': item['description']
                }

        question['categories'] = list(question['categories'].values())
        question['answers'] = list(question['answers'].values())

        parsed_questions.append(question)

    return parsed_questions


def process_user_answers(quiz_questions: List[QuestionWithAnswersForAdmin], answers: List[UserAnswer]):
    answers = sorted(answers, key=lambda answer: answer['question_id'])
    user_result = {
        'finished_at': datetime.now(),
        'answers': list(),
        'user_score': 0,
        'max_score': len(quiz_questions)
    }

    if len(answers) != len(quiz_questions):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='The number of user\'s answers does not correspond to the number of '
                                   'questions in the quiz')

    for i, answer in enumerate(answers):
        if answer['question_id'] != quiz_questions[i]['id']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='User\'s answers does not correspond to the questions of the quiz')

        user_result_item = {
            'question_id': answer['question_id'],
            'user_answer_id': answer['answer_id'],
            'correct_answer_id': quiz_questions[i]['id_1'],
            'is_correct': False
        }

        if answer['answer_id'] == quiz_questions[i]['id_1']:
            user_result['user_score'] += 1
            user_result_item['is_correct'] = True

        user_result['answers'].append(user_result_item)

    return user_result


def form_user_cache_key(email, quiz_id, finished_at):
    key = f'{email}:::{quiz_id}:::{str(finished_at)}'
    return key


def save_data_to_csv_file(data):
    data = json.loads(data)
    directory = 'csv-files'

    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)
    filename = f'details-{time().hex()}.csv'

    with open(f'{directory}/{filename}', 'w') as file:
        file.write('quiz_id;user_email;user_score;max_score;question_id;user_answer_id;'
                   'correct_answer_id;is_correct;finished_at\n')

        for answer in data['answers']:
            file.write(f"{data['quiz_id']};{data['user_email']};{data['user_score']};{data['max_score']};"
                       f"{answer['question_id']};{answer['user_answer_id']};{answer['correct_answer_id']};"
                       f"{answer['correct_answer_id']};{data['finished_at']}\n")

    return filename


class Auth0:
    @classmethod
    async def login(cls, user_creds: UserSignIn, session: ClientSession):
        payload = {
            'client_id': settings.CLIENT_ID,
            'client_secret': settings.CLIENT_SECRET,
            'audience': settings.AUDIENCE,
            'username': user_creds.email,
            'password': user_creds.password,
            'grant_type': 'password',
            'scope': 'openid offline_access'
        }
        url = f'https://{settings.DOMAIN}/oauth/token'

        async with session.post(url, json=payload) as response:
            result = await response.json()
            status_code = response.status

        return result, status_code

    @classmethod
    def verify(cls, token):
        jsonurl = urlopen("https://" + settings.DOMAIN + "/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}

        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=settings.ALGORITHMS,
                    audience=settings.AUDIENCE,
                    issuer="https://" + settings.DOMAIN + "/"
                )
            except jwt.ExpiredSignatureError:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Access token is expired')
            except jwt.JWTClaimsError:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail='Incorrect claims, please check the audience and issuer')
            except Exception:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unable to parse access token')

        return payload

    @classmethod
    async def register(cls, new_user_data: UserSignUp, session: ClientSession):
        payload = {
            'client_id': settings.CLIENT_ID,
            'connection': settings.CONNECTION,
            'email': new_user_data.email,
            'password': new_user_data.password,
            'name': new_user_data.name,
        }
        url = f'https://{settings.DOMAIN}/dbconnections/signup'

        async with session.post(url, json=payload) as response:
            result = await response.json()
            status_code = response.status

        return result, status_code
