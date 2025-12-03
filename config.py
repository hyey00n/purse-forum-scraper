"""
Purse Forum 크롤러 설정 파일
"""

# ============================================
# 가격 키워드 설정
# ============================================

# 가격 관련 키워드 (본문에서 찾을 단어들)
PRICE_KEYWORDS = "price,cost,paid,spent,total,usd,krw,won,dollar,$,₩"

# 시작 페이지 (1부터 시작)
START_PAGE = 1

# 최대 페이지 수
MAX_PAGES = 5

# 요청 간 대기 시간 (초)
DELAY_BETWEEN_REQUESTS = 3

# 타임아웃 설정 (초)
PAGE_LOAD_TIMEOUT = 45
ELEMENT_WAIT_TIMEOUT = 15

# ============================================
# 구글 시트 설정
# ============================================

# 구글 시트 ID
SPREADSHEET_ID = "YOUR_SPREADSHEET_ID_HERE"

# 시트 이름
SHEET_NAME = "Results"

# 구글 서비스 계정 인증 파일
GOOGLE_CREDENTIALS_FILE = "credentials.json"

# ============================================
# 병원 리스트 (한국 성형외과)
# ============================================

HOSPITAL_NAMES = [
    'Banobagi', 'View Plastic Surgery', 'ID Hospital', 'ID Plastic Surgery',
    'Braun', 'Wonjin', 'JK Plastic Surgery', 'Grand Plastic Surgery',
    'Item Plastic Surgery', 'Ever Clinic', 'April 31', 'Nana Plastic Surgery',
    'DA Plastic Surgery', 'BT Plastic Surgery', '365mc', 'Faceline',
    'Dream Plastic Surgery', 'Miho', 'TNTN', 'Opera',
    'Gangnam Beauty', 'Shimmian', 'Marble', 'Cinderella',
    'Petit', 'Wish', 'DAPRS', 'Premier', 'Renewal', 'Hershe', 'Original',
    'Glovi', 'Seojin', 'Yonsei Star', 'Apgujeong'
]

# ============================================
# 포럼 설정
# ============================================

FORUM_SECTION_ID = "277"