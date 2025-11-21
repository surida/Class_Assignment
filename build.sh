#!/bin/bash
# PyInstaller 빌드 스크립트 (Mac용)

echo "🔨 학급편성 프로그램 빌드 시작..."

# 이전 빌드 정리
rm -rf dist/학급편성.app build

# PyInstaller 실행 (PyQt6 GUI 버전, 콘솔 창 없음)
python3 -m PyInstaller \
    --onefile \
    --name="학급편성" \
    --windowed \
    --clean \
    class_assigner_gui_qt.py

echo ""
echo "✅ 빌드 완료!"
echo "📦 실행 파일 위치: dist/학급편성"
echo ""
echo "📋 배포 방법:"
echo "   1. dist/ 폴더의 '학급편성' 파일을 더블클릭"
echo "   2. GUI 창에서 파일 선택 버튼으로 입력 파일 지정"
echo "   3. 결과는 명단 파일과 같은 폴더에 자동 저장"
echo ""
