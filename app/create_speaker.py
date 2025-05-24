import outetts
import torch

# Initialize the interface
interface = outetts.Interface(
    config=outetts.ModelConfig(
        device='cpu',
        dtype=torch.float32
    )
)
wav_file = "bria_short.mp3"
transcript = "In the heart of an ancient forest, where the trees whispered secrets of the past, there lived a peculiar rabbit named Luna. Unlike any other rabbit, Luna was born with wings, a rare gift that she had yet to understand the purpose of."
speaker = interface.create_speaker(wav_file, transcript)
interface.save_speaker(speaker, "speaker.json")
