import asyncio
from io import BytesIO
from traceback import format_exc
from typing import Dict, List, Optional, Union
import environs
import os
import time

import nextcord
from nextcord.ext import commands, tasks
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

env = environs.Env()
env.read_env()


DISCORD_TOKEN = env.str("TOKEN")
COMMAND_PREFIX = env.str("PREFIX")
global is_connect_channel
is_connect_channel = False


bot = commands.Bot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    #task_loop.start()
    


# @tasks.loop(seconds=5)
# async def task_loop():
#     if is_connect_channel:
#         interaction = nextcord.Interaction()
#         while True:
#             start_recording(interaction)
#             await asyncio.sleep(5)

# connect command
@bot.slash_command(
    description="Connect to your voice channel or a specified voice channel.",
    dm_permission=False,
    default_member_permissions=8,  # admins only
)
async def connect(interaction: nextcord.Interaction, channel: Optional[Union[nextcord.VoiceChannel, nextcord.StageChannel]] = None,):
    assert interaction.guild
    assert isinstance(interaction.user, nextcord.Member)

    if interaction.guild.voice_client:
        await interaction.send("Voice is already connected.")
        return

    if channel:
        await channel.connect(recordable=True, prevent_leakage=True)
        await interaction.send(f"Connected to {channel.mention}")
        return

    author_voice: Optional[nextcord.VoiceState] = interaction.user.voice
    if author_voice and (channel := author_voice.channel):
        await author_voice.channel.connect(recordable=True, prevent_leakage=True)
        await interaction.send(f"Connected to your voice channel {channel.mention}")
        global is_connect_channel
        is_connect_channel = True
        return

    await interaction.send("You are not in a voice channel, and no voice channel was specified.")
    


# start recording command
@bot.slash_command(
    description="Start recording in the connected voice channel.",
    dm_permission=False,
    default_member_permissions=8,  # admins only
)
async def start_recording(interaction: nextcord.Interaction):
    assert interaction.guild
    assert isinstance(interaction.user, nextcord.Member)

    voice_client = interaction.guild.voice_client

    if not voice_client:
        await interaction.send("I am not connected to a voice channel. Use `/connect`")
        return

    if not isinstance(voice_client, RecorderClient):
        await interaction.send("I am not connected with a recordable client.")
        return

    await voice_client.start_recording()
    await interaction.send(f"Recording started in {voice_client.channel}")


# slash options for available export formats
# formats = nextcord.SlashOption(
#     name="export_format",
#     description="The format to export the recordings in.",
#     choices=[e.name for e in Formats],
# )

# stop recording command
@bot.slash_command(
    description="Stop recording in the connected voice channel.",
    dm_permission=False,
    default_member_permissions=8,  # admins only
)
async def stop_recording(
    interaction: nextcord.Interaction,
    export_format: str = "WAV",
    merge: bool = False,  # requires pydub
):
    assert interaction.guild
    assert isinstance(interaction.user, nextcord.Member)

    voice_client = interaction.guild.voice_client

    if not voice_client:
        await interaction.send("I am not connected to a voice channel.")
        return

    if not isinstance(voice_client, RecorderClient):
        await interaction.send("I am not connected with a recordable client.")
        return

    try:
        await interaction.response.defer()
        recordings = await voice_client.stop_recording(
            export_format=getattr(Formats, export_format),
            write_remaining_silence=True,  # makes sure the first track will fill length
        )
        assert not isinstance(recordings, AudioData)
    except Exception:
        print(exc := format_exc())
        await interaction.send(
            f"An error occured when exporting the recording\n```\n{exc[:1900]}\n```"
        )
        return

    if not recordings:
        await interaction.send("Export was unavailable.")
        return
    
    try:
        # await interaction.send(
        #     f"Recording stopped in {voice_client.channel}", files=list(recordings.values())
        # )
        #AudioFile.fp.writelines()
        try:
            os.mkdir("voicedata")
        except FileExistsError:
            pass
        for i in recordings.values():
            with open(os.path.join("voicedata", i.filename), "wb") as f:
                f.write(i.fp.read())
        
    except Exception:
        print(format_exc())
        await interaction.send(
            f"Recording stopped in {voice_client.channel} but failed to upload. Files may have been too large."
        )


bot.run(DISCORD_TOKEN)