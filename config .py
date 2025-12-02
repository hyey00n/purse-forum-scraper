"""
Purse Forum 크롤러 설정 파일
"""

# ============================================
# 검색 설정
# ============================================

# 검색 키워드 (여기를 수정하세요!)
SEARCH_KEYWORD = "rhinoplasty"

# 최대 페이지 수 (1-10 권장)
MAX_PAGES = 5

# 최대 스레드 수
MAX_THREADS = 50

# 요청 간 대기 시간 (초)
DELAY_BETWEEN_REQUESTS = 2

# ============================================
# 구글 시트 설정
# ============================================

# 구글 시트 ID (스프레드시트 URL에서 복사)
# https://docs.google.com/spreadsheets/d/[여기가_ID]/edit
SPREADSHEET_ID = "YOUR_SPREADSHEET_ID_HERE"

# 시트 이름
SHEET_NAME = "Results"

# 구글 서비스 계정 인증 파일 경로
GOOGLE_CREDENTIALS_FILE = "credentials.json"

# ============================================
# 병원 리스트 (한국 성형외과)
# ============================================

HOSPITAL_NAMES = [
    # 대형 유명 병원
    'Banobagi', 'View Plastic Surgery', 'ID Hospital', 'ID Plastic Surgery',
    'Braun', 'Wonjin', 'JK Plastic Surgery', 'Grand Plastic Surgery',
    'Item Plastic Surgery', 'Ever Clinic', 'April 31', 'Nana Plastic Surgery',
    'DA Plastic Surgery', 'BT Plastic Surgery', '365mc', 'Faceline',
    'Dream Plastic Surgery', 'Miho', 'TNTN', 'Opera',
    
    # 강남 유명 병원
    'Gangnam Beauty', 'Shimmian', 'Marble', 'Cinderella',
    'Petit', 'Wish', 'DAPRS',
    
    # 기타 유명 병원
    'Premier', 'Renewal', 'Hershe', 'Original',
    'Glovi', 'Seojin', 'Yonsei Star', 'Apgujeong',
    
    # 일반 표현
    'Korean Hospital', 'Korea Clinic', 'Seoul Clinic',
    'PS Hospital', 'Plastic Surgery Hospital'
]

# ============================================
# 포럼 설정
# ============================================

# Purse Forum 섹션 (Asian Plastic Surgery)
FORUM_SECTION_ID = "277"

# 검색 정렬 방식
SEARCH_ORDER = "relevance"

# ============================================
# 고급 설정
# ============================================

# 타임아웃 설정 (초)
PAGE_LOAD_TIMEOUT = 30
ELEMENT_WAIT_TIMEOUT = 10

# 디버그 모드
DEBUG_MODE = True

# 스크린샷 저장 (오류 발생 시)
SAVE_SCREENSHOTS = True
SCREENSHOT_DIR = "screenshots"