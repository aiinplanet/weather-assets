#!/bin/sh
# 사용법: sh tool/build.sh YYYY-MM-DD path/to/data.json [썸네일 시각(초), 기본 8.8]
# 영상·썸네일을 만들고 GitHub에 push한 뒤 raw 주소 두 개를 출력한다.
set -e
DATE="$1"; DATA="$2"; T="${3:-8.8}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
mkdir -p "$REPO/videos" "$REPO/images" "$REPO/data"
cp "$DATA" "$REPO/data/$DATE.json"
WX_DATA="$REPO/data/$DATE.json" python3 "$REPO/tool/render.py" "$REPO/videos/$DATE.mp4"
WX_DATA="$REPO/data/$DATE.json" WX_OUT="$TMP" python3 "$REPO/tool/render.py" still "$T"
ffmpeg -loglevel error -y -i "$TMP/still_$T.png" -q:v 3 "$REPO/images/$DATE.jpg"
cd "$REPO"
git add "videos/$DATE.mp4" "images/$DATE.jpg" "data/$DATE.json"
git commit -qm "Weather brief $DATE"
git push -q origin HEAD:main
B="https://raw.githubusercontent.com/aiinplanet/weather-assets/main"
echo "VIDEO_URL=$B/videos/$DATE.mp4"
echo "IMAGE_URL=$B/images/$DATE.jpg"
