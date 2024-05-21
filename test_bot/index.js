const { Client, GatewayIntentBits } = require('discord.js');
const { joinVoiceChannel, EndBehaviorType, VoiceConnectionStatus } = require('@discordjs/voice');
const fs = require('fs');
const prism = require('prism-media');
const { pipeline } = require('stream');
const ffmpeg = require('ffmpeg-static');
const { spawn } = require('child_process');
const sodium = require('libsodium-wrappers');  // Добавляем libsodium-wrappers для шифрования
const config = JSON.parse(fs.readFileSync('./config.json', 'utf8'));

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildVoiceStates,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildVoiceStates, // Добавляем intents для голосовых состояний
    GatewayIntentBits.GuildPresences
  ]
});

const TOKEN = config.discordToken;
const PREFIX = '!';

client.on('ready', () => {
    console.log("[" + new Date().toISOString() + "]", "Started!");
    // setStatus()
});

function setStatus() {
    client.user.setActivity(config.statusActivity, {
        type: config.statusType,
        url: config.statusURL
    });
    console.log(`Activity set to ${config.statusActivity}`);
}


client.on('messageCreate', async (message) => {
  if (message.content.startsWith(`${PREFIX}join`)) {
    if (message.member.voice.channel) {
      const connection = joinVoiceChannel({
        channelId: message.member.voice.channel.id,
        guildId: message.guild.id,
        adapterCreator: message.guild.voiceAdapterCreator,
        selfMute: false,
        selfDeaf: false
      });

      connection.on(VoiceConnectionStatus.Ready, () => {
        console.log('The bot has connected to the channel!');
      });

      const receiver = connection.receiver;

      receiver.speaking.on('start', (userId) => {
        console.log(`User ${userId} started speaking`);

        const audioStream = receiver.subscribe(userId, {
          end: {
            behavior: EndBehaviorType.AfterSilence,
            duration: 1000,
          },
        });
        const pcmStream = new prism.opus.Decoder({
            frameSize: 960,
            channels: 2,
            rate: 48000,
          });
  
          pipeline(audioStream, pcmStream, (err) => {
            if (err) {
              console.warn(`Error in PCM pipeline - ${err.message}`);
            }
          });
        

          const filePath = `./recordings/${userId}-${Date.now()}.ogg`;

          const ffmpegProcess = spawn(ffmpeg, [
            '-y', // Overwrite output files without asking
            '-f', 's16le', // Input format
            '-ar', '48000', // Set the audio sampling rate
            '-ac', '2', // Set the number of audio channels
            '-i', '-', // Input from stdin
            '-c:a', 'libopus', // Audio codec
            filePath, // Output file
          ]);
  
          pipeline(pcmStream, ffmpegProcess.stdin, (err) => {
            if (err) {
              console.warn(`Error recording file ${filePath} - ${err.message}`);
            } else {
              console.log(`Recorded ${filePath}`);
            }
          });
  
          ffmpegProcess.on('close', (code) => {
            if (code !== 0) {
              console.warn(`ffmpeg process exited with code ${code}`);
            }
          });
        });
      } else {
        message.reply('You need to join a voice channel first!');
      }
    } else if (message.content.startsWith(`${PREFIX}leave`)) {
      const connection = getVoiceConnection(message.guild.id);
      if (connection) {
        connection.destroy();
        message.reply('Left the voice channel!');
      } else {
        message.reply('I am not in a voice channel!');
      }
    }
  });
  
  client.login(TOKEN);
