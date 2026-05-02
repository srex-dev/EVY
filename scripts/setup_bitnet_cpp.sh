#!/bin/bash

# Install Microsoft's bitnet.cpp runtime and download the official BitNet
# b1.58 2B4T GGUF model for local EVY inference.

set -euo pipefail

: "${BITNET_REPO_URL:=https://github.com/microsoft/BitNet.git}"
: "${BITNET_DIR:=third_party/BitNet}"
: "${BITNET_MODEL_REPO:=microsoft/BitNet-b1.58-2B-4T-gguf}"
: "${BITNET_MODEL_DIR:=models/bitnet/BitNet-b1.58-2B-4T}"
: "${BITNET_QUANT_TYPE:=i2_s}"
: "${PYTHON:=python3}"

echo "Preparing BitNet runtime for EVY..."

if ! command -v git >/dev/null 2>&1; then
    echo "git is required"
    exit 1
fi

if ! command -v "${PYTHON}" >/dev/null 2>&1; then
    echo "${PYTHON} is required"
    exit 1
fi

mkdir -p "$(dirname "${BITNET_DIR}")" "${BITNET_MODEL_DIR}"
BITNET_DIR_PARENT="$(cd "$(dirname "${BITNET_DIR}")" && pwd)"
BITNET_DIR_ABS="${BITNET_DIR_PARENT}/$(basename "${BITNET_DIR}")"
MODEL_DIR_ABS="$(cd "${BITNET_MODEL_DIR}" && pwd)"

if [[ ! -d "${BITNET_DIR}/.git" ]]; then
    git clone --recursive "${BITNET_REPO_URL}" "${BITNET_DIR}"
else
    git -C "${BITNET_DIR}" pull --ff-only
    git -C "${BITNET_DIR}" submodule update --init --recursive
fi

"${PYTHON}" -m pip install -r "${BITNET_DIR}/requirements.txt"

if ! command -v huggingface-cli >/dev/null 2>&1; then
    "${PYTHON}" -m pip install "huggingface_hub[cli]"
fi

huggingface-cli download "${BITNET_MODEL_REPO}" --local-dir "${BITNET_MODEL_DIR}"

(
    cd "${BITNET_DIR_ABS}"
    "${PYTHON}" setup_env.py -md "${MODEL_DIR_ABS}" -q "${BITNET_QUANT_TYPE}"
)

cat > .env.bitnet << EOF
LLM_PROVIDER=bitnet
DEFAULT_MODEL=bitnet-b1.58-2B-4T
BITNET_MODEL=bitnet-b1.58-2B-4T
BITNET_CPP_DIR=/opt/bitnet.cpp
BITNET_MODEL_PATH=/models/bitnet/BitNet-b1.58-2B-4T/ggml-model-${BITNET_QUANT_TYPE}.gguf
BITNET_THREADS=2
BITNET_CONTEXT_TOKENS=512
BITNET_N_PREDICT=80
BITNET_ALLOW_FALLBACK=false
LLM_AUTO_PULL_MODELS=false
EOF

cat << EOF

BitNet setup complete.

Host runtime:
  ${BITNET_DIR}

Host model:
  ${BITNET_MODEL_DIR}/ggml-model-${BITNET_QUANT_TYPE}.gguf

Container env file:
  .env.bitnet

For lilEVY, run:
  docker compose --env-file .env.bitnet -f docker-compose.lilevy.yml up -d --build
EOF
