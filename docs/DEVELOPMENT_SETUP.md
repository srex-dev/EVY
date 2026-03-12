# EVY Development Setup Guide
## Local Development Environment Setup

### Purpose
Guide for setting up local development environment for EVY, including Rust and Python toolchains, testing, and debugging.

---

## 🛠️ **Development Environment**

### **Required Tools**

```bash
# Rust (latest stable)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup target add x86_64-unknown-linux-gnu  # For local dev
rustup target add aarch64-unknown-linux-gnu  # For ARM64 (Raspberry Pi)

# Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip

# Docker & Docker Compose
sudo apt install docker.io docker-compose

# Development Tools
sudo apt install git build-essential pkg-config libssl-dev
```

### **Project Setup**

```bash
# Clone repository
git clone https://github.com/srex-dev/EVY.git
cd EVY

# Python virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt  # Dev dependencies

# Rust projects
cd backend-rust
cargo build  # Build all Rust components
cd ..
```

---

## 🧪 **Running Tests**

```bash
# Python tests
pytest backend/tests/ -v

# Rust tests
cd backend-rust/sms_gateway && cargo test
cd ../message_router && cargo test
cd ../compression && cargo test
cd ../mesh_network && cargo test

# Integration tests
pytest backend/tests/test_integration.py -v

# Full test suite
pytest backend/tests/ tests/ -v --cov=backend
```

---

## 🐛 **Debugging**

### **Rust Debugging**
```bash
# Run with debug symbols
cargo build --debug

# Use GDB
gdb target/debug/sms_gateway

# Use logging
RUST_LOG=debug cargo run
```

### **Python Debugging**
```bash
# Use pdb
python -m pdb backend/services/llm_inference/main.py

# Use logging
export LOG_LEVEL=DEBUG
python backend/services/llm_inference/main.py
```

---

**END OF DEVELOPMENT SETUP**

## Addendum: Knowledge Bootstrap + Region

Generate knowledge artifacts and checksum manifest in one command:

```bash
python scripts/bootstrap_knowledge_base.py --region us
```

Output manifest:

- `data/lilevy/knowledge/knowledge_manifest.json`

## Addendum: Local-First Defaults

The edge profile now defaults to:

- `LLM_PROVIDER=ollama`
- `DEFAULT_MODEL=tinyllama`
- `BITNET_MODEL=bitnet-2b`
- `RAG_MIN_SIMILARITY=0.5`
- `LORA_FREQUENCY_MHZ=915.0` (US default)
