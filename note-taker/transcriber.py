from openai import OpenAI


def transcribe_basic(client: OpenAI, audio_path: str):
    """Transcribe an audio file using OpenAI Whisper API."""
    with open(audio_path, 'rb') as f:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
        )
    return response


def transcribe_with_prompt(client: OpenAI, audio_path: str, prompt: str):
    """Transcribe with a guiding prompt for improved accuracy."""
    with open(audio_path, 'rb') as f:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
            prompt=prompt,
        )
    return response


def transcribe_chunks(client: OpenAI, chunks: list[dict], prompt: str | None = None):
    """Transcribe each chunk and adjust timestamps to account for chunk offset."""
    all_segments = []

    for chunk_info in chunks:
        offset_s = chunk_info['start_ms'] / 1000

        with open(chunk_info['path'], 'rb') as f:
            kwargs = {
                'model': 'whisper-1',
                'file': f,
                'response_format': 'verbose_json',
                'timestamp_granularities': ['segment'],
            }
            if prompt:
                kwargs['prompt'] = prompt
            response = client.audio.transcriptions.create(**kwargs)

        for seg in response.segments:
            all_segments.append({
                'start': seg.start + offset_s,
                'end': seg.end + offset_s,
                'text': seg.text.strip(),
            })

    return all_segments
