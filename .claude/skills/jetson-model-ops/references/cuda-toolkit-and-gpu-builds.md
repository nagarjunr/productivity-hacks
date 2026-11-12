# CUDA toolkit and GPU builds on the Orin Nano (as tested on JetPack 7.2.1 / L4T R39.x; adapt the package versions to your release)

State to check first: `ls /usr/local/cuda*/bin/nvcc` (absent on a fresh board), `dpkg -l | grep -i cuda` (only the `nvidia-l4t-cuda*` runtime packages), `apt-cache search '^cuda-nvcc'`. The apt source `repo.download.nvidia.com/jetson/common r39.2` offers CUDA 13.2 packages; Ollama bundles its own CUDA libraries, so it does not need the toolkit.

## Minimal install (needs the owner's ok: it is a system-wide change)
1. Dry run: `apt-get -s install --no-install-recommends cuda-nvcc-13-2 cuda-cudart-dev-13-2 cuda-libraries-dev-13-2`. Expect about 40 new packages (cudart, nvrtc, cublas, cufft, curand, cusolver, cusparse, npp and their dev packages) and 0 upgraded or removed; stop and ask if the dry run removes anything.
2. Install detached so the SSH call returns: `setsid nohup sh -c 'sudo -n DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends <pkgs>; echo rc=$?; echo DONE > ~/cuda-install.done' > ~/cuda-install.log 2>&1 < /dev/null &`. `libcublas` alone is about 480 MB; on the slow link the whole install takes a long time and shares bandwidth with any other download.
3. Verify: `/usr/local/cuda/bin/nvcc --version`, then `ollama --version`, `systemctl is-active ollama`, `docker ps` (AnythingLLM healthy). Say so if any of them changed.

## GPU builds of C++ runtimes
- Build into a separate directory: `cmake -B build-cuda -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc -DCMAKE_CUDA_ARCHITECTURES=87 <project flag> && cmake --build build-cuda -j3`. Orin is compute capability 8.7. Use `-j3`, not all six cores: nvcc compiles of ggml-cuda are memory-heavy and the desktop and AnythingLLM are still running.
- Project flags (from each repo's build docs): `transcribe.cpp` `-DTRANSCRIBE_CUDA=ON -DTRANSCRIBE_BUILD_TOOLS=ON`; `qwentts.cpp` `-DGGML_CUDA=ON` (its `buildcuda.sh` wipes `build/`, so do not run it when CPU binaries are still needed); `stable-diffusion.cpp` `-DSD_CUDA=ON`. Without BLAS dev packages use the plain CPU build, not `buildcpu.sh` (it passes `-DGGML_BLAS=ON`).
- Find the binaries with `find <repo>/build-cuda -type f -name <bin>` (names: `transcribe-cli`, `qwen-tts`, `sd-cli`) and read the `.err` log of a run for CUDA backend lines to prove the GPU was used; a CUDA build that silently fell back to CPU looks identical in timing tables.
- Compare CPU and GPU with the same inputs: seconds per diffusion step (not total time when step counts differ), real-time factor for speech (processing time divided by audio duration), peak RSS from `resource.getrusage(RUSAGE_CHILDREN)` in a small wrapper.
- Speech round trip as a self-contained test: synthesize a known sentence with the TTS, resample to 16 kHz mono (numpy `interp` is enough for a test), transcribe with the ASR, compute word error rate against the sentence. `transcribe-cli` needs 16 kHz mono WAV. Parse only the text between `text:` and `segments:` in its output; scoring the whole stdout (header and timing lines included) gives a nonsense WER. Synthetic TTS audio mispronounces names, so also score the ASR on the repo's real-speech `samples/*.wav` (e.g. `jfk.wav`, known transcript) before judging the model; a synthetic-only run blamed the ASR for the TTS's errors.
- Torch for small models (Timestral 209M) runs on CPU in a venv. Before planning GPU PyTorch, run `python -c "import torch; print(torch.cuda.is_available())"` and read the warning: the stock PyPI aarch64 wheel (CUDA 13 build) prints that no published build supports compute capability 8.7. Check the Jetson AI Lab index for a `jp7` torch wheel with `pip install --dry-run --no-deps torch --index-url <index>` in a throwaway venv (delete it after) before downloading anything large.
- Look at generated images yourself with an image-capable model in the main session (prompt match, artifacts, CPU vs GPU step counts); an unattended report job only sees file sizes and timings.
- Queue heavy benchmarks behind a gate file (`while [ ! -f go_bench ]; do sleep 15; done`): start the network-bound pulls at once, run quick interactive checks while they download, then create the gate so memory-sensitive and headless benches start only after those checks end.

## Exact sources for the runtimes and packages named above

Clone or install only from these; do not trust a package found by name alone.

- `transcribe.cpp` (speech to text): https://github.com/handy-computer/transcribe.cpp
- `qwentts.cpp` (text to speech): https://github.com/ServeurpersoCom/qwentts.cpp
- `stable-diffusion.cpp` (image diffusion): https://github.com/leejet/stable-diffusion.cpp
- Timestral (time-series forecaster): model https://huggingface.co/mistralai/Timestral-209M, code https://github.com/mistralai/timestral (installed here with `pip install git+https://github.com/mistralai/timestral.git`)
- Package names and CMake flags above were read from each repository's own build documentation on the day of the test; check the repository again before relying on them, since flags change.

