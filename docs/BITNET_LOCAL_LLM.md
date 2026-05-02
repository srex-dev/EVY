# BitNet Local 1-Bit LLM

EVY will use Microsoft BitNet b1.58 2B4T as the target local 1-bit/1.58-bit LLM for lilEVY.

Authoritative project links:

- BitNet runtime: [microsoft/BitNet](https://github.com/microsoft/BitNet)
- GGUF model: [microsoft/BitNet-b1.58-2B-4T-gguf](https://huggingface.co/microsoft/BitNet-b1.58-2B-4T-gguf)

## Decision

The local LLM target is:

- Provider: `bitnet`
- Runtime: `bitnet.cpp`
- Model: `bitnet-b1.58-2B-4T`
- Quantized model file: `ggml-model-i2_s.gguf`
- Default container model path: `/models/bitnet/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf`
- Default container runtime path: `/opt/bitnet.cpp`

This replaces TinyLlama as the preferred lilEVY local LLM. TinyLlama/Ollama remain useful fallback and development options, but they are no longer the intended field model.

## Why This Fits EVY

BitNet is a better match for lilEVY than a traditional 4-bit tiny model because EVY needs local reasoning on CPU-class edge hardware, short SMS responses, and low power draw. The official model is MIT-licensed, and the official runtime is designed around the specialized kernels needed for BitNet inference.

## What Changed In The Repo

- `LLM_PROVIDER` now defaults to `bitnet`.
- `DEFAULT_MODEL` now defaults to `bitnet-b1.58-2B-4T`.
- `backend/services/llm_inference/bitnet_cpp_manager.py` calls the local `bitnet.cpp` runtime.
- The LLM health endpoint reports whether the BitNet runtime and model file are present.
- `docker-compose.lilevy.yml` mounts:
  - `./models/bitnet` to `/models/bitnet`
  - `./third_party/BitNet` to `/opt/bitnet.cpp`
- `deploy-lilevy.sh` writes BitNet settings into `.env.lilevy`.
- `scripts/setup_bitnet_cpp.sh` prepares the runtime and model directory.

## Setup On Linux Or Raspberry Pi

Run:

```bash
bash scripts/setup_bitnet_cpp.sh
```

The script:

- Clones or updates `microsoft/BitNet` into `third_party/BitNet`.
- Installs the BitNet Python requirements.
- Downloads the official GGUF model from Hugging Face.
- Runs BitNet setup for the `i2_s` quantization.
- Writes `.env.bitnet`.

Then start the core lilEVY stack:

```bash
docker compose --env-file .env.bitnet -f docker-compose.lilevy.yml up -d --build
```

Or use the helper:

```bash
./deploy-lilevy.sh
```

## Validation Script

After setup, validate the host runtime and model file:

```bash
python scripts/validate_bitnet_local_llm.py
```

Run one direct local inference through `bitnet.cpp`:

```bash
python scripts/validate_bitnet_local_llm.py --run-inference
```

If the lilEVY LLM service is already running, also check the service health contract:

```bash
python scripts/validate_bitnet_local_llm.py --health-url http://127.0.0.1:18002/health
```

Each run writes a JSON report to:

```text
data/lilevy/software_reports/bitnet_local_llm_report.json
```

## SMS Prompt Benchmark

After the BitNet service is running, run the 20-prompt SMS benchmark:

```bash
python scripts/benchmark_bitnet_sms_prompts.py
```

The default benchmark calls `http://127.0.0.1:18002/inference`, expects every response to fit within 160 characters, and uses a default p95 latency threshold of 45 seconds:

```bash
python scripts/benchmark_bitnet_sms_prompts.py --p95-threshold-seconds 45
```

The report is written to:

```text
data/lilevy/software_reports/bitnet_sms_benchmark_report.json
```

## Health Check

Check the LLM service:

```bash
curl http://127.0.0.1:18002/health
```

The response should include:

- `details.provider = bitnet`
- `details.bitnet.available = true`
- `details.bitnet.model_present = true`
- `details.bitnet.runtime_present = true`

If `available` is false, the service will not silently use a cloud model. The default is `BITNET_ALLOW_FALLBACK=false` so missing local model setup is visible before field testing.

## Hardware Notes

For first hardware testing, keep the BitNet settings conservative:

- `BITNET_THREADS=2`
- `BITNET_CONTEXT_TOKENS=512`
- `BITNET_N_PREDICT=80`

Increase only after measuring CPU load, response latency, memory use, and battery draw on the actual Raspberry Pi.

## Open Validation Items

- Measure cold-start model load time on the target Pi.
- Measure p50/p95 response time for 20 real SMS-style prompts using `scripts/benchmark_bitnet_sms_prompts.py`.
- Measure power draw during idle, model load, and inference.
- Decide whether `BITNET_THREADS=2` is enough or whether a Pi 5 can safely use more cores.
- Verify the Docker path after `bitnet.cpp` is compiled on the same CPU architecture as the runtime container.
- Capture and archive `bitnet_local_llm_report.json` after the first successful local inference.
- Capture and archive `bitnet_sms_benchmark_report.json` after the first successful 20-prompt benchmark.
