init python:
    import urllib.request
    import json
    import ssl
    import os
    import time
    import base64

    class StoryGenerator:
        def __init__(self):
            self.context = []
            self.API_KEY = "YOUR_API_KEY"
            self.headers = {
                "Authorization": f"Bearer {self.API_KEY}",
                "Content-Type": "application/json"
            }
            self.ssl_context = ssl.create_default_context()
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE

        def generate_image(self, prompt):
            image_dir = os.path.join(renpy.config.gamedir, "images")

            data = {
                "model": "dall-e-3",
                "prompt": f"ANIME STYLE, {prompt}",
                "n": 1,
                "size": "1024x1024",
                "quality": "hd"
            }

            try:
                req = urllib.request.Request(
                    "https://api.openai.com/v1/images/generations",
                    data=json.dumps(data).encode('utf-8'),
                    headers=self.headers,
                    method='POST'
                )

                with urllib.request.urlopen(req, context=self.ssl_context) as response:
                    result = json.loads(response.read().decode('utf-8'))

                    if 'data' in result and len(result['data']) > 0:
                        image_url = result['data'][0]['url']

                        timestamp = int(time.time())
                        filename = f"generated_image_{timestamp}.png"
                        filepath = os.path.join(image_dir, filename)
                        return_filepath = os.path.join("images", filename)

                        image_req = urllib.request.Request(image_url)
                        with urllib.request.urlopen(image_req, context=self.ssl_context) as img_response:
                            with open(filepath, 'wb') as f:
                                f.write(img_response.read())
                        return return_filepath
            except Exception as e:
                error_msg = f"이미지 생성 오류: {str(e)}"
                return error_msg

        def generate_story(self, current_situation, player_choice):
            self.context.append({
                "situation": current_situation,
                "choice": player_choice
            })
            context_history = self.context[-3:]  # 최근 3개의 컨텍스트만 유지

            messages = [
                {
                    "role": "system",
                    # "content": "당신은 흥미진진한 시각소설을 만드는 스토리텔러입니다. JSON 형식으로 다음 전개와 선택지를 제공해주세요."
                    "content": "당신은 흥미진진하고 두근두근한 연애 시뮬레이션을 만드는 스토리텔러입니다. 여러 아름다운 여자들을 만나는 것을 목표로 합니다. JSON 형식으로 다음 전개와 선택지를 제공해주세요."
                },
                {
                    "role": "user",
                    "content": f"""
                    이전 상황: {json.dumps(context_history, ensure_ascii=False)}
                    현재 상황: {current_situation}
                    플레이어 선택: {player_choice}

                    다음과 같은 JSON 형식으로 응답해주세요:
                    {{
                        "narrative": "다음 장면 서술, 200자 이내",
                        "choices": ["선택지1", "선택지2", "선택지3"],
                        "prompt": "다음 장면을 바탕으로 DALL-E 3 이미지 생성 프롬프트, 영어로 작성"
                    }}
                    """
                }
            ]

            data = {
                "model": "gpt-4o",
                "messages": messages
            }

            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=json.dumps(data).encode('utf-8'),
                headers=self.headers,
                method='POST'
            )

            try:
                with urllib.request.urlopen(req, context=self.ssl_context) as response:
                    api_response = json.loads(response.read().decode('utf-8'))
                    content = api_response["choices"][0]["message"]["content"]
                    result = self._parse_response(content)
                    image = self.generate_image(result["prompt"])
                    return result, image
            except Exception as e:
                return {
                    "narrative": f"스토리를 가져오는데 실패했습니다: {str(e)}",
                    "choices": ["다시 시도하기"],
                }, None

        def _parse_response(self, response):
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                return json.loads(json_str)
            except Exception as e:
                return {
                    "narrative": f"죄송합니다. 일시적인 오류가 발생했습니다: {str(e)}",
                    "choices": ["다시 시도하기"],
                }, None

    story_generator = StoryGenerator()

define narrator = Character('진행자', color="#c8ffc8")

# 게임 시작
label start:
    # $ current_situation = "당신은 신비로운 모험을 시작하려 합니다."
    # $ player_choice = "모험을 시작한다"

    $ current_situation = "당신은 오늘 오후 10시에 열리는 친구의 생일파티에 초대되었습니다."
    $ player_choice = "파티에 참석한다"

    menu:
        narrator "[current_situation]"

        "[player_choice]":
            pass

    while True:
        $ response, image = story_generator.generate_story(current_situation, player_choice)

        scene black
        if image:
            show expression "[image]" at center

        narrator "[response['narrative']]"

        # 선택지를 미리 변수에 저장
        $ choices = response['choices']

        menu:
            "다음 행동을 선택하세요"

            "[choices[0]]":
                $ player_choice = choices[0]
                $ current_situation = response['narrative']

            "[choices[1]]":
                $ player_choice = choices[1]
                $ current_situation = response['narrative']

            "[choices[2]]":
                $ player_choice = choices[2]
                $ current_situation = response['narrative']