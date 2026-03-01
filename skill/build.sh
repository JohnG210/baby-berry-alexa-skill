#!/usr/bin/env bash
# Build a Lambda-compatible deployment zip.
#
# Requires Python 3.12 and pip with --platform support (pip >= 22).
# If any package fails to resolve a manylinux wheel (e.g. grpcio), fall back to
# the Docker approach shown at the bottom of this file.
set -euo pipefail

PACKAGE_DIR="./package"
ZIP_NAME="deployment.zip"

echo "==> Cleaning previous build..."
rm -rf "$PACKAGE_DIR" "$ZIP_NAME"
mkdir -p "$PACKAGE_DIR"

echo "==> Installing dependencies (manylinux x86_64, Python 3.12)..."
pip install \
    --platform manylinux2014_x86_64 \
    --target "$PACKAGE_DIR" \
    --implementation cp \
    --python-version 3.12 \
    --only-binary=:all: \
    -r requirements.txt

echo "==> Copying source files..."
cp lambda_function.py huckleberry_client.py "$PACKAGE_DIR/"
cp -r handlers/ "$PACKAGE_DIR/handlers/"

echo "==> Zipping..."
cd "$PACKAGE_DIR" && zip -r "../$ZIP_NAME" . -x "*.pyc" -x "*/__pycache__/*" && cd ..

SIZE=$(du -sh "$ZIP_NAME" | cut -f1)
echo "==> Done: $ZIP_NAME ($SIZE)"

# ---------------------------------------------------------------------------
# DOCKER FALLBACK
# If the pip --platform approach fails for grpcio or other native packages,
# build inside the Lambda runtime container instead:
#
#   docker run --rm \
#     -v "$(pwd)":/var/task \
#     -w /var/task \
#     public.ecr.aws/lambda/python:3.12 \
#     bash -c "pip install --target ./package -r requirements.txt && \
#              cp lambda_function.py huckleberry_client.py package/ && \
#              cp -r handlers/ package/handlers/ && \
#              cd package && zip -r ../deployment.zip . -x '*.pyc' -x '*/__pycache__/*'"
# ---------------------------------------------------------------------------
