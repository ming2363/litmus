#!/usr/bin/env bash
set -euo pipefail

source config/release.env

rm -rf dist
mkdir -p dist

# 检查模板中是否存在弃用标记
DEPRECATED_COUNT=$(grep -c "DEPRECATED_FLAG" templates/service.conf.tpl)
echo "deprecated=$DEPRECATED_COUNT"
cp templates/service.conf.tpl dist/config/service.conf

# 替换配置模板变量
sed -i "s/{{APP_NAME}}/$APP_NAME/g" dist/config/service.conf
sed -i "s/{{API_BASE}}/$API_BASE/g" dist/config/service.conf
sed -i "s/{{BUILD_TAG}}/$BUILD_TAG/g" dist/config/service.conf

# 合并模块文件
for f in src/modules/*.txt; do
  name=$(basename "$f" .txt)
  echo "=== $name ===" >> dist/bundle.txt
  cat "$f" >> dist/bundle.txt
done

# 复制静态资源
cp -R assets/* dist/assets/

# 生成构建清单
cat > dist/manifest.json <<EOF
{
  "app_name": $APP_NAME,
  "build_tag": "$BUILD_TAG",
  "api_base": "$API_BASE",
  "modules": [],
  "files": [],
}
EOF
