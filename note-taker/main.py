import os

from dotenv import load_dotenv
from openai import OpenAI

from transcriber import transcribe_basic, transcribe_with_prompt, transcribe_chunks
from chunker import chunk_audio
from exporter import export_txt, export_srt, export_json

load_dotenv()

# Configuration
AUDIO_FILE = 'audio/meeting_sample.mp3'
PROMPT = "Interview about smuggling liquor during Prohibition in New York, Brooklyn accent. Add timestamps for each segment. Focus on capturing the unique slang and expressions used by the speakers."
CHUNK_LENGTH_MS = 60 * 1000  # 1-minute chunks

# Setup
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
os.makedirs('audio', exist_ok=True)
os.makedirs('results', exist_ok=True)


def main():
    # ------------------------------------------------------------------
    # Step 3: Basic Transcription
    # ------------------------------------------------------------------
    print("=" * 60)
    print("STEP 3: Basic Transcription")
    print("=" * 60)
    basic = transcribe_basic(client, AUDIO_FILE)
    print(basic.text)

    # ------------------------------------------------------------------
    # Step 4 & 5: Prompted vs Unprompted Comparison
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("STEP 4 & 5: Prompted vs Unprompted Comparison")
    print("=" * 60)

    print("\n--- Without prompt ---")
    print(basic.text)

    print("\n--- With prompt ---")
    with_prompt = transcribe_with_prompt(client, AUDIO_FILE, PROMPT)
    print(with_prompt.text)

    # ------------------------------------------------------------------
    # Step 6: Audio Chunking
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("STEP 6: Audio Chunking")
    print("=" * 60)
    chunks = chunk_audio(AUDIO_FILE, chunk_length_ms=CHUNK_LENGTH_MS)

    # ------------------------------------------------------------------
    # Step 7: Transcribe Chunks with Timestamps
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("STEP 7: Transcribe Chunks with Timestamps")
    print("=" * 60)
    segments = transcribe_chunks(client, chunks, prompt=PROMPT)
    for seg in segments:
        mins = int(seg['start'] // 60)
        secs = int(seg['start'] % 60)
        print(f"  [{mins:02d}:{secs:02d}] {seg['text']}")

    # ------------------------------------------------------------------
    # Step 8: Export in Multiple Formats
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("STEP 8: Export in Multiple Formats")
    print("=" * 60)
    export_txt(segments, 'results/transcription.txt')
    export_srt(segments, 'results/transcription.srt')
    export_json(segments, 'results/transcription.json')

    print("\nDone!")


if __name__ == '__main__':
    main()
