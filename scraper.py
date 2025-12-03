"""
Purse Forum 크롤러
Asian Plastic Surgery 포럼에서 데이터 수집 → 구글 시트 저장
"""

import sys
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import *

# 즉시 출력 설정
def log(message):
    """즉시 출력되는 로그"""
    print(message, flush=True)

class PurseForumScraper:
    def __init__(self):
        log("🔧 초기화 시작...")
        self.collected_urls = set()
        self.results = []
        
        try:
            self.setup_driver()
            self.setup_google_sheets()
            log("✅ 초기화 완료!")
        except Exception as e:
            log(f"❌ 초기화 실패: {e}")
            raise
    
    def setup_driver(self):
        """Chrome 드라이버 설정"""
        log("🌐 Chrome 드라이버 설정 중...")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # 타임아웃 설정
        self.driver.set_page_load_timeout(30)
        self.driver.implicitly_wait(10)
        
        self.wait = WebDriverWait(self.driver, 10)
        log("✅ Chrome 드라이버 설정 완료 (타임아웃: 30초)")
    
    def setup_google_sheets(self):
        """구글 시트 연결 설정"""
        log("📊 구글 시트 연결 중...")
        
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                GOOGLE_CREDENTIALS_FILE, 
                scope
            )
            
            log(f"📋 스프레드시트 ID: {SPREADSHEET_ID}")
            
            self.gc = gspread.authorize(creds)
            self.sheet = self.gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
            
            # 헤더 설정
            headers = ['제목', 'URL', '작성자', '작성일', '본문 내용', '가격 정보', '병원', '수집일시']
            
            if not self.sheet.row_values(1):
                self.sheet.update('A1:H1', [headers])
                self.sheet.format('A1:H1', {
                    'backgroundColor': {'red': 0.26, 'green': 0.52, 'blue': 0.96},
                    'textFormat': {'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}, 'bold': True}
                })
            
            log("✅ 구글 시트 연결 완료")
            
        except Exception as e:
            log(f"❌ 구글 시트 연결 실패: {e}")
            raise
    
    def search_forum(self, keyword):
        """포럼 섹션 접속"""
        log(f"\n🔍 Asian Plastic Surgery 포럼 접속 중...")
        
        forum_url = "https://forum.purseblog.com/forums/asian-plastic-surgery-cosmetic-procedures.277/"
        
        try:
            log(f"🌐 URL: {forum_url}")
            log("⏳ 페이지 로딩 대기 중... (최대 30초)")
            
            self.driver.get(forum_url)
            
            log("⏰ 5초 대기...")
            time.sleep(5)
            
            log(f"✅ 페이지 로드 완료!")
            log(f"📍 현재 URL: {self.driver.current_url}")
            log(f"📄 페이지 제목: {self.driver.title}")
            
        except TimeoutException:
            log(f"❌ 타임아웃: 페이지 로드가 30초 초과")
            log("🔧 포럼 사이트가 느리거나 봇을 차단했을 수 있습니다")
            raise
        except Exception as e:
            log(f"❌ 페이지 로드 실패: {e}")
            raise
    
    def collect_thread_links(self, max_pages=5, start_page=1):
        """스레드 링크 수집 (모든 스레드)"""
        log(f"\n📋 링크 수집 중... ({start_page}페이지부터 {max_pages}페이지까지)")
        
        # 시작 페이지로 이동 (1페이지가 아닌 경우)
        if start_page > 1:
            log(f"➡️ {start_page}페이지로 건너뛰는 중...")
            for skip in range(1, start_page):
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, 'a.pageNav-jump--next')
                    next_button.click()
                    time.sleep(2)
                    log(f"✅ {skip + 1}페이지로 이동")
                except NoSuchElementException:
                    log(f"⚠️ {skip}페이지에서 다음 버튼을 찾을 수 없음")
                    break
                except Exception as e:
                    log(f"❌ 페이지 건너뛰기 실패: {e}")
                    break
        
        for page in range(start_page, max_pages + 1):
            try:
                log(f"\n--- 페이지 {page} ---")
                
                thread_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/threads/"]')
                log(f"🔗 발견된 링크 수: {len(thread_links)}")
                
                page_urls = []
                for link in thread_links:
                    try:
                        url = link.get_attribute('href')
                        if url and '/threads/' in url:
                            clean_url = url.split('?')[0].split('#')[0]
                            if clean_url not in self.collected_urls:
                                self.collected_urls.add(clean_url)
                                page_urls.append(clean_url)
                    except:
                        continue
                
                log(f"✅ 페이지 {page}: {len(page_urls)}개 새 링크 발견")
                
                # 다음 페이지
                if page < max_pages:
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, 'a.pageNav-jump--next')
                        log("➡️ 다음 페이지로 이동...")
                        next_button.click()
                        time.sleep(2)
                    except NoSuchElementException:
                        log("⚠️ 다음 페이지 없음 (마지막 페이지)")
                        break
                        
            except Exception as e:
                log(f"❌ 페이지 {page} 처리 중 오류: {e}")
                break
        
        log(f"\n✅ 총 {len(self.collected_urls)}개 링크 수집 완료")
    
    def extract_thread_content(self, url):
        """개별 스레드 본문 추출"""
        try:
            self.driver.get(url)
            time.sleep(2)
            
            # 제목
            try:
                title = self.driver.find_element(By.CSS_SELECTOR, 'h1.p-title-value').text
            except:
                title = "No title"
            
            # 작성자
            try:
                author = self.driver.find_element(By.CSS_SELECTOR, 'a.username').text
            except:
                author = "Unknown"
            
            # 작성일
            try:
                date = self.driver.find_element(By.CSS_SELECTOR, 'time').get_attribute('datetime')
            except:
                date = ""
            
            # 본문 내용
            try:
                content_div = self.driver.find_element(By.CSS_SELECTOR, 'div.bbWrapper')
                content = content_div.text
                
                content = re.sub(r'\n{3,}', '\n\n', content)
                content = content.strip()
                
                if len(content) > 45000:
                    content = content[:45000] + "\n\n... (본문 너무 길어 일부만 표시)"
                    
            except:
                content = "No content"
            
            # 가격 정보 추출
            prices = self.extract_prices(title + " " + content)
            price_info = ", ".join(prices) if prices else "No price"
            
            # 병원 정보 추출
            hospitals = self.extract_hospitals(title + " " + content)
            hospital_info = ", ".join(hospitals) if hospitals else "No hospital"
            
            return {
                'title': title,
                'url': url,
                'author': author,
                'date': date,
                'content': content,
                'price': price_info,
                'hospital': hospital_info
            }
            
        except Exception as e:
            log(f"❌ 본문 추출 실패 ({url}): {e}")
            return None
    
    def extract_prices(self, text):
        """가격 정보 추출"""
        prices = set()
        
        patterns = [
            r'\$[\d,]+(?:\.\d{2})?',
            r'[\d,]+\s*(?:usd|USD|dollars?)',
            r'₩[\d,]+',
            r'[\d,]+\s*(?:won|KRW)',
            r'\$?[\d]+\.?\d*k',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            prices.update(matches)
        
        return list(prices)[:10]
    
    def extract_hospitals(self, text):
        """병원 이름 추출"""
        text_lower = text.lower()
        found_hospitals = []
        
        for hospital in HOSPITAL_NAMES:
            if hospital.lower() in text_lower:
                found_hospitals.append(hospital)
        
        return list(set(found_hospitals))[:5]
    
    def save_to_sheet(self):
        """구글 시트에 저장 (가격 정보 있는 것만)"""
        if not self.results:
            log("⚠️ 저장할 데이터가 없습니다.")
            return
        
        # 가격 관련 키워드
        price_keywords = ['price', 'cost', 'paid', 'spent', 'total', 'usd', 'krw', 'won', 'dollar', '$', '₩']
        
        # 가격 정보가 있는 게시글만 필터링
        filtered_results = []
        for result in self.results:
            text = (result['title'] + " " + result['content']).lower()
            
            # 가격 정보가 있거나 가격 키워드가 있으면 포함
            has_price = result['price'] != "No price"
            has_keyword = any(keyword in text for keyword in price_keywords)
            
            if has_price or has_keyword:
                filtered_results.append(result)
                log(f"✅ 가격 정보 발견: {result['title'][:50]}")
            else:
                log(f"⏭️ 가격 없음 건너뜀: {result['title'][:50]}")
        
        if not filtered_results:
            log("⚠️ 가격 정보가 있는 게시글이 없습니다.")
            return
        
        log(f"\n💾 구글 시트에 {len(filtered_results)}개 데이터 저장 중... (전체 {len(self.results)}개 중)")
        
        try:
            existing_rows = len(self.sheet.get_all_values())
            
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            rows = []
            
            for result in filtered_results:
                row = [
                    result['title'],
                    result['url'],
                    result['author'],
                    result['date'],
                    result['content'],
                    result['price'],
                    result['hospital'],
                    now
                ]
                rows.append(row)
            
            if rows:
                start_row = existing_rows + 1
                cell_range = f'A{start_row}:H{start_row + len(rows) - 1}'
                self.sheet.update(cell_range, rows)
                
                log(f"✅ {len(rows)}개 데이터 저장 완료!")
                log(f"📊 구글 시트: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")
                
        except Exception as e:
            log(f"❌ 구글 시트 저장 실패: {e}")
            
    def run(self, keyword, max_pages=5, max_threads=50, start_page=1):
        """메인 실행"""
        log("=" * 60)
        log("🚀 Purse Forum 크롤러 시작")
        log("=" * 60)
        
        try:
            # 1. 포럼 접속
            self.search_forum(keyword)
            
            # 2. 링크 수집 (start_page부터 시작)
            self.collect_thread_links(max_pages, start_page)
            
            if len(self.collected_urls) == 0:
                log("⚠️ 수집된 링크가 없습니다!")
                return
            
            # 3. 본문 수집
            log(f"\n📖 본문 수집 시작... (최대 {max_threads}개)")
            
            urls_to_process = list(self.collected_urls)[:max_threads]
            
            for i, url in enumerate(urls_to_process, 1):
                log(f"\n[{i}/{len(urls_to_process)}] {url}")
                
                result = self.extract_thread_content(url)
                
                if result:
                    self.results.append(result)
                    log(f"✅ 수집 완료: {result['title'][:50]}...")
                
                if i < len(urls_to_process):
                    time.sleep(DELAY_BETWEEN_REQUESTS)
            
            # 4. 구글 시트 저장
            self.save_to_sheet()
            
            log("\n" + "=" * 60)
            log("✅ 크롤링 완료!")
            log(f"📊 총 수집: {len(self.results)}개")
            log("=" * 60)
            
        except Exception as e:
            log(f"\n❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            try:
                self.driver.quit()
                log("🔒 브라우저 종료")
            except:
                pass

if __name__ == "__main__":
    log("=" * 60)
    log("프로그램 시작!")
    log("=" * 60)
    
    try:
        scraper = PurseForumScraper()
        scraper.run(
            keyword=SEARCH_KEYWORD,
            max_pages=MAX_PAGES,
            max_threads=MAX_THREADS,
            start_page=START_PAGE
        )
    except Exception as e:
        log(f"❌ 프로그램 실행 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)