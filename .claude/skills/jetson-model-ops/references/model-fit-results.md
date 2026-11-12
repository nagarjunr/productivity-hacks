# What fits on the Jetson Orin Nano 8 GB (7.3 GiB unified), measured

Measured on one board (JetPack 7.2.1) in November 2026. Your numbers will differ with versions, desktop load and power mode; treat this as a starting point and extend it with your own runs.

Ollama 0.40.11, Q4_K_M files, 4K context unless noted, five-task benchmark (competence and speed only). Desktop and a 1.5 GB AnythingLLM container running unless noted. Extend this table when a model is tested; keep one line per model.

| Model | File | Result | Lowest free memory |
|---|---|---|---|
| Qwen3.8-4B-Distill (empero-ai, hf.co GGUF) | 2.8 GB | 5/5 thinking, 4/5 non-thinking (the miss was an over-strict check); about 10 tok/s; first load 116 s | about 1.3 GB |
| Qwen3.5-4B (official `qwen3.5:4b`) | 3.3 GB | 5/5 thinking, 4/5 non-thinking (real miss on the trick question); about 10 tok/s; load 38 s | about 0.77 GB |
| Qwythos-9B-v2 MTP (hf.co GGUF) | 5.9 GB | OOM-killed beside desktop and containers; ran only headless, 1K context, 6.6 tok/s, under 0.5 GB free | about 0.49 GB |
| Nemotron-3.5-Bolt-E4B (NVIDIA, hf.co GGUF) | 6.18 GB | OOM on the first prompt even headless with 6.4 GB free at 2K context (NvMap allocation failed) | not usable |
| Gemma 4 E2B (official `gemma4:e2b`, includes vision and audio encoders) | 4.6 GB | 0/5 in both modes beside desktop and AnythingLLM: `cudaMalloc failed: out of memory`, runner stopped; headless retry not yet done | 44-127 MB |

Rules of thumb from these runs:
- Q4 files up to about 3.5 GB are comfortable beside the desktop and AnythingLLM; 5.9 GB and above needs the desktop stopped and still may not load; 6+ GB did not load at all.
- A repo named '4GB' or '4B effective' can ship a file well over 5 GB; read the file size from the Hugging Face API first.
- Thinking mode multiplies tokens: a three-bullet answer took 1,686 tokens (168 s) and a short function 2,098 tokens (216 s). Keep thinking off for chat and retrieval; use it only for hard reasoning.
- Speed here (about 10 tok/s for 4B Q4) includes the load of a running desktop and a container; a clean headless system is likely faster (not measured here).
- Qwen3.5-architecture GGUFs (including MTP variants) load in Ollama 0.32.14 and later; the MTP head is not used by Ollama.

## Triage of a Hugging Face link list

For each repo call `/api/models/<repo>?blobs=true` and sum the `.gguf` sizes per quant folder (multi-shard repos list shards of 40-130 GB each; one shard is not the model). Then sort:
- **Fits (about 3.5 GB or less, Ollama-runnable):** small dense LLMs at Q4. Check whether they beat what is already installed before downloading; an older 4B (Qwen3-4B, 2.5 GB) usually does not.
- **Marginal (5-6 GB):** headless only, 1-2K context, and the 6.2 GB class already failed. Say so instead of promising.
- **Too big, by size alone:** a 27B needs 16-24 GB of VRAM (smallest 2-bit file about 10 GB, Q4 about 18 GB); NVFP4 files target Blackwell-class GPUs; 100B+ MoE models start at 46 GB for 1-bit quants and run 95-335 GB for the rest. Names like 'Nano' or 'Flash' say nothing: one 'Nano' repo's main files were 13-16 GB, and its 2 GB file was a speculative-decoding draft model.
- **Not chat models, so no tokens/s:** speech-to-text (Nemotron ASR 0.6B, 0.5 GB Q4, runtime `transcribe.cpp`), text-to-speech (Qwen3-TTS, 0.9 GB for 0.6B talker plus tokenizer, runtime `qwentts.cpp`), time-series forecasting (Mistral Timestral-209M, 0.84 GB, `pip install` of the `timestral` package, runs on CPU), image diffusion (SD 1.5 class 2.1 GB via `stable-diffusion.cpp`). Judge these by real-time factor, seconds per diffusion step, or forecast error against a naive baseline.
- **Does not fit and needs extras:** a pixel-space diffusion model whose full checkpoint is 12 GB and whose pipeline also needs a 4B vision-language text encoder, with an experimental GGUF loader in ComfyUI, is out of scope for 7.3 GiB.
- **Gated repos** (README returns 401) cannot be inspected; say the model's purpose is unverified.
- Runtime repos (MIT/Apache) build from source with `cmake`; check the repo's push date and licence, and whether the model weights carry a different licence ('other').
- Uncensored or abliterated re-uploads are edits of someone else's model: mention provenance and that safety was not reviewed.

## Sources of the models measured above

Each of these was pulled and run on the board used for the table. Use the exact IDs, since look-alike repositories exist.

- Qwen3.8-4B-Distill: https://huggingface.co/empero-ai/Qwen3.8-4B-Distill-GGUF (`ollama pull hf.co/empero-ai/Qwen3.8-4B-Distill-GGUF:Q4_K_M`)
- Qwythos-9B-v2 MTP: https://huggingface.co/empero-ai/Qwythos-9B-v2-GGUF
- Qwen3.5-4B: https://ollama.com/library/qwen3.5 (`ollama pull qwen3.5:4b`)
- Gemma 4 E2B: https://ollama.com/library/gemma4 (`ollama pull gemma4:e2b`)
- Nemotron-3.5-Bolt-E4B: https://ollama.com/library/nemotron-3.5-bolt
- Speech and image models named in the triage section: Nemotron ASR 0.6B GGUF https://huggingface.co/handy-computer/nemotron-3.5-asr-streaming-0.6b-gguf, Qwen3-TTS GGUF https://huggingface.co/Serveurperso/Qwen3-TTS-GGUF, Timestral-209M https://huggingface.co/mistralai/Timestral-209M, OpenJourney https://huggingface.co/prompthero/openjourney

