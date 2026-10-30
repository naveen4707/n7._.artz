# Loomis AI — Member 2.4 Generative Enhancement

M2.4 is an optional generative layer placed AFTER the deterministic Loomis
renderer.

Pipeline:

reference image
→ Member 1 structural analysis
→ construction.json
→ deterministic graphite renderer
→ M2.4 generative enhancement

The deterministic renderer remains the guaranteed fallback.

## Install

From `E:\LoomisAI\ai-engine`:

```powershell
pip install openai
```

Set the API key as an environment variable. Do not put it in source code.

PowerShell for the current terminal session:

```powershell
$env:OPENAI_API_KEY="YOUR_REAL_KEY"
$env:LOOMIS_IMAGE_MODEL="gpt-image-2"
```

## Test the prompt without using the API

```powershell
python src\generative\generate_stage.py --stage 1 --print-prompt
```

## Generate one stage

```powershell
python src\generative\generate_stage.py --stage 1
```

Input:

```text
output\hand_drawn\stage_01.png
```

Output:

```text
output\generative\stage_01.png
```

## Generate all seven stages

Run them one at a time initially:

```powershell
python src\generative\generate_stage.py --stage 1
python src\generative\generate_stage.py --stage 2
python src\generative\generate_stage.py --stage 3
python src\generative\generate_stage.py --stage 4
python src\generative\generate_stage.py --stage 5
python src\generative\generate_stage.py --stage 6
python src\generative\generate_stage.py --stage 7
```

Do NOT replace the deterministic outputs. M2.4 writes to:

```text
output\generative\
```

so we can compare:

```text
output\hand_drawn\stage_XX.png
output\generative\stage_XX.png
```

This makes it easy to reject a generated result if it changes the Loomis
geometry too much.
