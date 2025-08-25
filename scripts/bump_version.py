#!/usr/bin/env python3
"""
버전 업데이트 스크립트

사용법:
    python scripts/bump_version.py 0.2.0
    python scripts/bump_version.py patch  # 0.1.0 -> 0.1.1
    python scripts/bump_version.py minor  # 0.1.0 -> 0.2.0  
    python scripts/bump_version.py major  # 0.1.0 -> 1.0.0
"""

import sys
import re
from pathlib import Path

def get_current_version():
    """pyproject.toml에서 현재 버전 읽기"""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text(encoding="utf-8")
    
    match = re.search(r'version = "([^"]+)"', content)
    if match:
        return match.group(1)
    else:
        raise ValueError("pyproject.toml에서 버전을 찾을 수 없습니다")

def parse_version(version_str):
    """버전 문자열을 major.minor.patch로 파싱"""
    parts = version_str.split(".")
    if len(parts) != 3:
        raise ValueError(f"잘못된 버전 형식: {version_str}")
    
    return [int(p) for p in parts]

def bump_version_part(current_version, bump_type):
    """버전의 특정 부분을 증가"""
    major, minor, patch = parse_version(current_version)
    
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor": 
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"알 수 없는 bump_type: {bump_type}")

def update_version_in_file(new_version):
    """pyproject.toml의 버전 업데이트"""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text(encoding="utf-8")
    
    # 버전 라인 찾아서 교체
    new_content = re.sub(
        r'version = "[^"]+"',
        f'version = "{new_version}"',
        content
    )
    
    pyproject_path.write_text(new_content, encoding="utf-8")
    print(f"✅ pyproject.toml 버전을 {new_version}으로 업데이트했습니다")

def main():
    if len(sys.argv) != 2:
        print("사용법: python scripts/bump_version.py <version|major|minor|patch>")
        sys.exit(1)
    
    current_version = get_current_version()
    print(f"현재 버전: {current_version}")
    
    version_arg = sys.argv[1]
    
    # 직접 버전 지정 또는 bump 타입 지정
    if version_arg in ["major", "minor", "patch"]:
        new_version = bump_version_part(current_version, version_arg)
    else:
        # 직접 버전 지정
        new_version = version_arg
        # 버전 형식 검증
        try:
            parse_version(new_version)
        except ValueError as e:
            print(f"❌ {e}")
            sys.exit(1)
    
    print(f"새로운 버전: {new_version}")
    
    # 확인
    response = input("버전을 업데이트하시겠습니까? (y/N): ")
    if response.lower() != 'y':
        print("취소되었습니다")
        sys.exit(0)
    
    # 업데이트 실행
    update_version_in_file(new_version)
    
    print(f"""
🎉 버전 업데이트 완료!

다음 단계:
1. git add pyproject.toml
2. git commit -m "Bump version to {new_version}"
3. git tag v{new_version}
4. git push origin main --tags
    """)

if __name__ == "__main__":
    main()
