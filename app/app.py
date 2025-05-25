from typing import Optional

import aiofiles
import outetts
import torch
from fastapi import FastAPI, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from langdetect import detect
from pyflac import FileEncoder as AudioEncoder
from tokenizer import multilingual_cleaners

STYLES = [
    {"style": "BOLD", "regex": r"\*\*(.*?)\*\*", "offset": 2},
    {"style": "ITALIC", "regex": r"\*(.*?)\*", "offset": 1},
    {"style": "MONOSPACE", "regex": r"\`\`(.*?)\`\`", "offset": 2},
]

app = FastAPI()
server_host = "http://localhost:8000"
origins = ["*", server_host, "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

device = "cuda" if torch.cuda.is_available() else "cpu"
interface = outetts.Interface(
    outetts.ModelConfig.auto_config(
        model=outetts.Models.VERSION_1_0_SIZE_1B,
        backend=outetts.Backend.LLAMACPP,
        quantization=outetts.LlamaCppQuantization.FP16,
    )
)
speaker = interface.load_speaker("bria.json")


@app.get("/")
async def read_root():
    return {"device": device}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/tts")
async def tts(
    text: str = Form(None, description="Text to convert to speech."),
    compress: Optional[bool] = Form(True, description="Compress the audio into FLAC."),
):
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text to convert into speech must be provided.",
        )

    async with aiofiles.tempfile.NamedTemporaryFile(
        mode="w+t", delete=True, suffix=".wav"
    ) as output_wav:
        wav_file = output_wav.name
        lang_code = detect(text)

        if not lang_code:
            lang_code = "en"

        output = interface.generate(
            config=outetts.GenerationConfig(
                text=multilingual_cleaners(text, lang_code),
                generation_type=outetts.GenerationType.CHUNKED,
                speaker=speaker,
                sampler_config=outetts.SamplerConfig(
                    temperature=0.8,
                    min_p=0.0,
                ),
                max_batch_size=32,
                server_host=server_host,
            )
        )
        output.save(wav_file)

        if compress:
            async with aiofiles.tempfile.NamedTemporaryFile(
                mode="w+t", delete=True, suffix=".flac"
            ) as output_flac:
                flac_file = output_flac.name
                encoder = AudioEncoder(input_file=wav_file, output_file=flac_file)
                encoder.process()
                encoder.finish()

                async with aiofiles.open(flac_file, "rb") as flac:
                    content = await flac.read()
                    return Response(content=content, media_type="audio/flac")

        async with aiofiles.open(wav_file, "rb") as audio:
            content = await audio.read()
            return Response(content=content, media_type="audio/wav")
