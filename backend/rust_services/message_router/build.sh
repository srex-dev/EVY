#!/bin/bash
# Build script for EVY Message Router (Rust)

set -e

echo "Building EVY Message Router (Rust)..."

# Check if Rust is installed
if ! command -v cargo &> /dev/null; then
    echo "Error: Rust/Cargo not found. Please install Rust from https://rustup.rs/"
    exit 1
fi

# Build release version
echo "Building release version..."
cargo build --release

# Build with Python bindings if requested
if [ "$1" == "--python" ]; then
    echo "Building with Python bindings..."
    cargo build --release --features python
    
    echo ""
    echo "Python bindings built. To install:"
    echo "  pip install ."
fi

echo ""
echo "Build complete! Binary location:"
echo "  target/release/libevy_message_router.so (or .dylib/.dll)"
echo ""
echo "To run tests:"
echo "  cargo test"

