#!/bin/bash

# lilEVY deployment script.
# Starts the core edge SMS profile defined in docker-compose.lilevy.yml.

set -euo pipefail

if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD=(docker-compose)
else
    echo "Docker Compose is required. Install Docker Compose v2 or docker-compose v1."
    exit 1
fi

: "${NODE_ID:=lilevy-001}"
: "${GSM_DEVICE:=/dev/ttyUSB0}"
: "${GSM_BAUD_RATE:=115200}"
: "${DEFAULT_MODEL:=bitnet-b1.58-2B-4T}"
: "${LLM_PROVIDER:=bitnet}"
: "${BITNET_MODEL:=bitnet-b1.58-2B-4T}"
: "${BITNET_CPP_DIR:=/opt/bitnet.cpp}"
: "${BITNET_MODEL_PATH:=/models/bitnet/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf}"
: "${BITNET_THREADS:=2}"
: "${BITNET_CONTEXT_TOKENS:=512}"
: "${BITNET_N_PREDICT:=80}"
: "${BITNET_ALLOW_FALLBACK:=false}"
: "${LLM_AUTO_PULL_MODELS:=false}"
: "${MAX_SMS_PER_MINUTE:=10}"
: "${MAX_SMS_PER_HOUR:=100}"
: "${RAG_MIN_SIMILARITY:=0.5}"
: "${LILEVY_API_PORT:=18080}"
: "${LILEVY_SMS_PORT:=18000}"
: "${LILEVY_ROUTER_PORT:=18001}"
: "${LILEVY_LLM_PORT:=18002}"
: "${LILEVY_RAG_PORT:=18003}"
: "${LILEVY_PRIVACY_PORT:=18004}"

export NODE_ID GSM_DEVICE GSM_BAUD_RATE DEFAULT_MODEL LLM_PROVIDER
export BITNET_MODEL BITNET_CPP_DIR BITNET_MODEL_PATH BITNET_THREADS
export BITNET_CONTEXT_TOKENS BITNET_N_PREDICT BITNET_ALLOW_FALLBACK
export LLM_AUTO_PULL_MODELS
export MAX_SMS_PER_MINUTE MAX_SMS_PER_HOUR RAG_MIN_SIMILARITY
export LILEVY_API_PORT LILEVY_SMS_PORT LILEVY_ROUTER_PORT
export LILEVY_LLM_PORT LILEVY_RAG_PORT LILEVY_PRIVACY_PORT

echo "Deploying lilEVY core edge profile..."

if [[ "$(uname -m)" != "aarch64" && "$(uname -m)" != "armv7l" ]]; then
    echo "Warning: lilEVY is intended for ARM edge hardware; continuing on $(uname -m)."
fi

echo "Creating runtime directories..."
mkdir -p data/lilevy/{knowledge,chroma,privacy,metrics,models/embedding_cache,telemetry}
mkdir -p models/tiny models/bitnet third_party logs

if [[ -e "$GSM_DEVICE" ]]; then
    echo "Configuring GSM device permissions for $GSM_DEVICE..."
    sudo chmod 666 "$GSM_DEVICE" || true
    sudo usermod -a -G dialout "$USER" || true
else
    echo "GSM device $GSM_DEVICE was not found. SMS hardware access will wait for a local override/device."
fi

if [[ -e /dev/spidev0.0 ]]; then
    sudo chmod 666 /dev/spidev0.0 || true
fi

if command -v raspi-config >/dev/null 2>&1; then
    echo "Enabling Raspberry Pi SPI interface..."
    sudo raspi-config nonint do_spi 0 || true
fi

echo "Writing .env.lilevy..."
cat > .env.lilevy << EOF
NODE_TYPE=lilevy
NODE_ID=${NODE_ID}
GSM_DEVICE=${GSM_DEVICE}
GSM_BAUD_RATE=${GSM_BAUD_RATE}
LOG_LEVEL=INFO
DEFAULT_MODEL=${DEFAULT_MODEL}
LLM_PROVIDER=${LLM_PROVIDER}
BITNET_MODEL=${BITNET_MODEL}
BITNET_CPP_DIR=${BITNET_CPP_DIR}
BITNET_MODEL_PATH=${BITNET_MODEL_PATH}
BITNET_THREADS=${BITNET_THREADS}
BITNET_CONTEXT_TOKENS=${BITNET_CONTEXT_TOKENS}
BITNET_N_PREDICT=${BITNET_N_PREDICT}
BITNET_ALLOW_FALLBACK=${BITNET_ALLOW_FALLBACK}
LLM_AUTO_PULL_MODELS=${LLM_AUTO_PULL_MODELS}
MAX_SMS_PER_MINUTE=${MAX_SMS_PER_MINUTE}
MAX_SMS_PER_HOUR=${MAX_SMS_PER_HOUR}
RAG_MIN_SIMILARITY=${RAG_MIN_SIMILARITY}
LILEVY_API_PORT=${LILEVY_API_PORT}
LILEVY_SMS_PORT=${LILEVY_SMS_PORT}
LILEVY_ROUTER_PORT=${LILEVY_ROUTER_PORT}
LILEVY_LLM_PORT=${LILEVY_LLM_PORT}
LILEVY_RAG_PORT=${LILEVY_RAG_PORT}
LILEVY_PRIVACY_PORT=${LILEVY_PRIVACY_PORT}
EOF

COMPOSE_FILES=(-f docker-compose.lilevy.yml)
if [[ -f docker-compose.override.yml ]]; then
    COMPOSE_FILES+=(-f docker-compose.override.yml)
fi

if [[ "$LLM_PROVIDER" != "bitnet" ]] && command -v ollama >/dev/null 2>&1; then
    echo "Ensuring local model is available in Ollama: ${DEFAULT_MODEL}"
    ollama pull "${DEFAULT_MODEL}" || true
elif [[ "$LLM_PROVIDER" == "bitnet" ]]; then
    echo "Using BitNet local LLM. Run scripts/setup_bitnet_cpp.sh before hardware field testing."
fi

echo "Building lilEVY images..."
"${COMPOSE_CMD[@]}" --env-file .env.lilevy "${COMPOSE_FILES[@]}" build

echo "Starting lilEVY services..."
"${COMPOSE_CMD[@]}" --env-file .env.lilevy "${COMPOSE_FILES[@]}" up -d

echo "Checking service health..."
declare -A SERVICE_PORTS=(
    ["api-gateway"]="${LILEVY_API_PORT}"
    ["sms-gateway"]="${LILEVY_SMS_PORT}"
    ["message-router"]="${LILEVY_ROUTER_PORT}"
    ["tiny-llm"]="${LILEVY_LLM_PORT}"
    ["local-rag"]="${LILEVY_RAG_PORT}"
    ["privacy-filter"]="${LILEVY_PRIVACY_PORT}"
)

for service in "${!SERVICE_PORTS[@]}"; do
    port="${SERVICE_PORTS[$service]}"
    ok=false
    for _ in {1..30}; do
        if curl -fsS "http://127.0.0.1:${port}/health" >/dev/null 2>&1; then
            ok=true
            break
        fi
        sleep 2
    done
    if [[ "$ok" == "true" ]]; then
        echo "OK: $service is healthy on port $port"
    else
        echo "ERROR: $service did not become healthy on port $port"
        "${COMPOSE_CMD[@]}" --env-file .env.lilevy "${COMPOSE_FILES[@]}" ps
        exit 1
    fi
done

echo "lilEVY deployment status:"
"${COMPOSE_CMD[@]}" --env-file .env.lilevy "${COMPOSE_FILES[@]}" ps

cat << EOF

lilEVY deployment completed.

Service URLs:
  API Gateway:     http://127.0.0.1:${LILEVY_API_PORT}
  SMS Gateway:     http://127.0.0.1:${LILEVY_SMS_PORT}
  Message Router:  http://127.0.0.1:${LILEVY_ROUTER_PORT}
  Tiny LLM:        http://127.0.0.1:${LILEVY_LLM_PORT}
  Local RAG:       http://127.0.0.1:${LILEVY_RAG_PORT}
  Privacy Filter:  http://127.0.0.1:${LILEVY_PRIVACY_PORT}

Management:
  Logs:    ${COMPOSE_CMD[*]} --env-file .env.lilevy ${COMPOSE_FILES[*]} logs -f
  Stop:    ${COMPOSE_CMD[*]} --env-file .env.lilevy ${COMPOSE_FILES[*]} down
  Restart: ${COMPOSE_CMD[*]} --env-file .env.lilevy ${COMPOSE_FILES[*]} restart
EOF
