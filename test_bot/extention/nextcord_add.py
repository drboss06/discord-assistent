import asyncio
from io import BytesIO
from traceback import format_exc
from typing import Dict, List, Optional, Union
import environs
import os
import nextcord
from nextcord.ext import commands
from nextcord.voice_recording import (
    AUDIO_CHANNELS,
    AUDIO_HZ,
    AudioData,
    AudioFile,
    Formats,
    RecorderClient,
    Silence,
    get_ffmpeg_format,
)


def merge_audio(audio_files: Dict[int, AudioFile], format: Formats) -> Optional[nextcord.File]:
    try:
        import pydub  # pip install pydub
    except ImportError:
        print("pydub is not installed. Install pydub with `pip install pydub`")

    if not audio_files or len(audio_files) == 1:
        return None

    # format all AudioFiles into AudioSegments
    segments: List[tuple[pydub.AudioSegment, Optional[Silence]]] = [
        (
            pydub.AudioSegment.from_file(
                f.fp,
                format=str(f.filename).rsplit(".", 1)[-1],
                sample_width=AUDIO_CHANNELS,
                frame_rate=AUDIO_HZ,
                channels=AUDIO_CHANNELS,
            ),
            f.starting_silence,
        )
        for f in audio_files.values()
    ]

    # get the first segment, which will have a starting silence of `None`
    index, first_segment = next(
        iter((i, seg[0]) for i, seg in enumerate(segments) if seg[1] is None)
    )
    del segments[index]

    # merge
    for seg, start in segments:
        first_segment = first_segment.overlay(seg, position=int(start.milliseconds) if start else 0)

    # export the merged track
    final = BytesIO()
    format_str = format.name.lower()
    first_segment.export(final, format=get_ffmpeg_format(format_str))

    # seek all tracks to start
    final.seek(0)
    for f in audio_files.values():
        f.fp.seek(0)

    return nextcord.File(final, f"merged.{format_str}", force_close=True)
