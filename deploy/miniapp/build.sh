#!/bin/bash
# 韧翎成长计划统一小程序 - 一键构建脚本

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MINIAPP_DIR="$PROJECT_ROOT/apps/unified-miniapp"
BUILD_OUTPUT="$MINIAPP_DIR/dist/build/mp-weixin"

echo "=========================================="
echo "韧翎成长计划统一小程序 - 构建脚本"
echo "=========================================="

# 检查 pnpm
if ! command -v pnpm &> /dev/null; then
    echo "错误: 未安装 pnpm"
    echo "请运行: npm install -g pnpm"
    exit 1
fi

echo ""
echo "[1/4] 检查依赖..."
cd "$PROJECT_ROOT"
if [ ! -d "node_modules" ]; then
    echo "安装依赖中..."
    pnpm install
else
    echo "依赖已安装"
fi

echo ""
echo "[2/4] 清理旧构建..."
if [ -d "$BUILD_OUTPUT" ]; then
    rm -rf "$BUILD_OUTPUT"
    echo "已清理旧构建产物"
fi

echo ""
echo "[3/4] 构建小程序..."
pnpm -C "$MINIAPP_DIR" build:mp-weixin

echo ""
echo "[4/4] 验证构建产物..."
if [ -f "$BUILD_OUTPUT/app.js" ] && [ -f "$BUILD_OUTPUT/app.json" ]; then
    echo "✓ 构建成功"
    echo ""
    echo "构建产物位置:"
    echo "  $BUILD_OUTPUT"
    echo ""
    echo "下一步:"
    echo "  1. 打开微信开发者工具"
    echo "  2. 导入项目: $BUILD_OUTPUT"
    echo "  3. 点击上传按钮发布"
else
    echo "✗ 构建失败: 未找到必需文件"
    exit 1
fi

echo ""
echo "=========================================="
echo "构建完成"
echo "=========================================="
