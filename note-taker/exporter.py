import json
from datetime import timedelta


def _format_srt_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format HH:MM:SS,mmm."""
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def export_txt(segments: list[dict], output_path: str) -> None:
    """Export transcription as human-readable text with [MM:SS] timestamps."""
    with open(output_path, 'w') as f:
        for seg in segments:
            mins = int(seg['start'] // 60)
            secs = int(seg['start'] % 60)
            f.write(f"[{mins:02d}:{secs:02d}] {seg['text']}\n")
    print(f"Exported TXT  -> {output_path}")


def export_srt(segments: list[dict], output_path: str) -> None:
    """Export transcription in SRT subtitle format."""
    with open(output_path, 'w') as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n")
            f.write(f"{_format_srt_timestamp(seg['start'])} --> {_format_srt_timestamp(seg['end'])}\n")
            f.write(f"{seg['text']}\n\n")
    print(f"Exported SRT  -> {output_path}")


def export_json(segments: list[dict], output_path: str) -> None:
    """Export transcription as JSON."""
    with open(output_path, 'w') as f:
        json.dump({'segments': segments}, f, indent=2)
    print(f"Exported JSON -> {output_path}")
