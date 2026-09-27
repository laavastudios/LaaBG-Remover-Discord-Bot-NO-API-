# LaaBG Remover Discord Bot

A local-first Discord background-removal bot written entirely in Python.

## Commands

- `.help` — Components V2 help panel
- `.bgremove` — ask the user for an image and return a transparent PNG
- `.ping` — WebSocket latency
- `.about` — creator/project information

## Processing engine

LaaBG uses **rembg** with a local ONNX model. No commercial background-removal API is used and uploaded images are not intentionally persisted by the bot.

The default model is `birefnet-general`. rembg currently provides multiple local models including BiRefNet, U²-Net, IS-Net and portrait/anime variants. Models are downloaded locally on first use and reused through a persistent model directory.

For a lighter machine, use:

```env
BG_MODEL=birefnet-general-lite
```

For people:

```env
BG_MODEL=birefnet-portrait
```

## Install

Python 3.11–3.13 is supported by current rembg releases.

### Windows

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
copy .env.example .env
```

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

Then set `DISCORD_TOKEN` in `.env` and run:

```bash
python bot.py
```

The `rembg[cpu]` extra installs the CPU ONNX Runtime backend explicitly, avoiding the common “no ONNX runtime backend” setup problem.

## Discord permissions

Enable **Message Content Intent** in the Discord Developer Portal.

The bot needs:

- View Channels
- Send Messages
- Read Message History
- Attach Files

## Emoji system

Every UI surface supports custom emoji aliases.

An alias can be:

- Unicode: `✅`
- Current-server emoji name: `laava_success`
- Bot application emoji name: `laava_success`
- Emoji ID
- Full `<:name:id>` or `<a:name:id>` markup

The resolver checks the current guild first, then application-owned emojis, then uses a Unicode fallback.

The bot fetches application emojis at startup using discord.py's application-emoji API.

## Components V2

The UI uses discord.py's `LayoutView`, `Container`, `TextDisplay`, `Separator`, and `ActionRow`. These are Discord V2 layout components supported by discord.py 2.6+.

## Security / reliability

- Bot token is read only from `.env`.
- `.env` is ignored by Git.
- Input is capped by bytes and decoded pixel count.
- Only supported image formats are accepted.
- Download timeout is enforced.
- Model processing timeout is enforced.
- Only one model inference runs at a time.
- The loaded rembg session is reused instead of creating a model session for every image.
- Output is verified as a valid PNG before upload.
- Errors shown to users are sanitized; technical details go to logs.

## Model licensing

The bot's code and rembg are separate from individual model-weight licenses. Do not assume every available model has the same license. In particular, rembg documents a separate BRIA license restriction for `bria-rmbg`, so this project intentionally does **not** use that model by default. Check the specific model license before commercial redistribution.

## Project

Created by **LaavaBee / Laava Studios**.

- https://github.com/laavastudios
- https://laavastudios.live
