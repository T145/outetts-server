import requests

compress = False

en_test = """The average distance between the Earth and Jupiter varies as both planets follow elliptical orbits around the Sun.
The closest point, known as perihelion, occurs when the two planets are about 465 million miles (746 million kilometers) apart, while the farthest point, aphelion, is around 928 million miles (1.5 billion kilometers) away."""
kr_test = "추석은 내가 가장 좋아하는 명절이다. 나는 며칠 동안 휴식을 취하고 친구 및 가족과 시간을 보낼 수 있습니다."
fr_test = """Je comprends le français et je suis capable de répondre dans cette langue ! Il y a une petite erreur dans votre phrase : vous avez écrit « e toi » au lieu de « et toi », et « tappele » semble être une confusion avec « t'appelles ».

Si vous souhaitez continuer la conversation en français, je serai ravie d'essayer de vous aider. Êtes-vous intéressé(e) à pratiquer cette langue ou avez-vous une question spécifique?"""
music = "♪ In the jungle, the mighty jungle, the lion barks tonight ♪"

tests = {
    "en_test": en_test,
    "kr_test": kr_test,
    "fr_test": fr_test,
    "music": music
}
sound_format = "flac" if compress else "wav"

for key, test in tests.items():
    response = requests.post(url="http://localhost:8000/tts", data={
        "text": test,
        "compress": compress
    })

    with open(f"{key}.{sound_format}", mode="bw") as f:
        f.write(response.content)
