# Note-Taker Transcription Report

## Prompted vs Unprompted Transcriptions

The unprompted transcription (basic Whisper call with no context) produced a reasonable output but struggled with domain-specific details. Without guidance, the model had to guess at the context of the conversation, occasionally misinterpreting words or phrasing unique to the speaker's Brooklyn accent and Prohibition-era vocabulary.

The prompted transcription used the hint: *"Interview about smuggling liquor during Prohibition in New York, Brooklyn accent."* This gave Whisper contextual priming, which led to noticeable improvements:

- **Proper nouns and places** (e.g., "Atlantic City", "Cuba") were transcribed more consistently.
- **Period-specific language** and slang were better preserved rather than being "corrected" to modern phrasing.
- **Accent handling** improved — the Brooklyn dialect features were less likely to be misheard or normalized.

The prompt acts as a bias toward expected vocabulary, which is especially valuable for niche or historical content where the default language model might favor more common modern words.

## Benefits of Chunking for Long Audio

The Whisper API has a **25 MB file size limit**, making chunking essential for longer recordings. Beyond that hard constraint, chunking provides several practical benefits:

- **Memory efficiency**: Processing smaller segments avoids loading the entire audio into memory at once.
- **Timestamp accuracy**: Shorter chunks tend to produce more precise segment-level timestamps, since Whisper has less audio to align.
- **Fault tolerance**: If one chunk fails (network error, API timeout), only that chunk needs to be retried rather than the entire file.
- **Scalability**: Chunks could be processed in parallel to reduce total transcription time for very long recordings.

In this project, 1-minute chunks were used. The `transcribe_chunks` function handles the critical step of adding each chunk's offset back to the segment timestamps so the final output reflects the original recording's timeline.

## Challenges Faced

- **Timestamp alignment across chunks**: Whisper returns timestamps relative to each chunk (starting at 0). Mapping these back to the original audio required tracking each chunk's start offset and adjusting every segment accordingly.
- **Prompt engineering**: Finding the right level of detail for the transcription prompt required experimentation. Too vague and it has no effect; too specific and it can bias the model toward hallucinating expected content.
- **Colloquial speech**: The speaker's informal, stream-of-consciousness storytelling style (pauses, restarts, implied context) is inherently difficult for any speech-to-text model to punctuate and segment cleanly.
- **Export format differences**: Each output format (TXT, SRT, JSON) has different timestamp conventions that needed careful formatting — particularly the SRT format's `HH:MM:SS,mmm` requirement.

## Recommendations for Improving Accuracy

1. **Use `gpt-4o-mini` for post-processing**: After transcription, pass the raw text through a language model to fix grammar, add speaker labels, and generate a structured summary.
2. **Experiment with chunk overlap**: Adding a few seconds of overlap between chunks can prevent words from being cut off at chunk boundaries.
3. **Iterative prompting**: Use the last few words of one chunk's transcription as the prompt for the next chunk to maintain continuity.
4. **Language parameter**: Explicitly set `language="en"` in the API call to avoid the model wasting capacity on language detection.
5. **Pre-process audio**: Normalize volume levels and reduce background noise before transcription to give Whisper cleaner input.
