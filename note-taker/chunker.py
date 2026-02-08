import os

from pydub import AudioSegment


def chunk_audio(audio_path: str, chunk_length_ms: int = 10 * 60 * 1000,
                output_dir: str = 'audio') -> list[dict]:
    """Split an audio file into chunks of `chunk_length_ms` milliseconds.

    Returns a list of dicts: {path, start_ms, end_ms}.
    """
    audio = AudioSegment.from_file(audio_path)
    chunks = []

    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i + chunk_length_ms]
        idx = i // chunk_length_ms
        chunk_path = os.path.join(output_dir, f'chunk_{idx}.mp3')
        chunk.export(chunk_path, format='mp3')

        end_ms = min(i + chunk_length_ms, len(audio))
        chunks.append({
            'path': chunk_path,
            'start_ms': i,
            'end_ms': end_ms,
        })
        print(f"  Chunk {idx}: {i / 1000:.1f}s – {end_ms / 1000:.1f}s")

    print(f"Created {len(chunks)} chunk(s)")
    return chunks
