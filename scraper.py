"""
Purse Forum 크롤러
키워드 검색 → 본문 수집 → 구글 시트 저장
"""

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

class PurseForumScraper:
    def __init__(self):
        self.setup_driver()
        self.setup_google_sheets()
        self.collected_urls = set()
        self.results = []
        
    def setup_driver(self):
        """Chrome 드라이버 설정"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        print("✅ Chrome 드라이버 설정 완료")
        
    def setup_google_sheets(self):
        """구글 시트 연결 설정"""
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                GOOGLE_CREDENTIALS_FILE, 
                scope
            )
            
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
            
            print("✅ 구글 시트 연결 완료")
            
        except Exception as e:
            print(f"❌ 구글 시트 연결 실패: {e}")
            raise
    
    def search_forum(self, keyword):
        """포럼 검색"""
        print(f"\n🔍 검색 시작: '{keyword}'")
        
        search_url = f"https://forum.purseblog.com/search/search?keywords={keyword}&c[nodes][0]=277&order=relevance"
        
        self.driver.get(search_url)
        time.sleep(3)
        
        print(f"📄 페이지 로드 완료: {self.driver.current_url}")
        
    def collect_thread_links(self, max_pages=5):
        """스레드 링크 수집"""
        print(f"\n📋 링크 수집 중... (최대 {max_pages}페이지)")
        
        for page in range(1, max_pages + 1):
            try:
                print(f"\n--- 페이지 {page} ---")
                
                thread_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/threads/"]')
                
                page_urls = []
                for link in thread_links:
                    try:
                        url = link.get_attribute('href')
                        if url and '/threads/' in url and url not in self.collected_urls:
                            clean_url = url.split('?')[0].split('#')[0]
                            if clean_url not in self.collected_urls:
                                self.collected_urls.add(clean_url)
                                page_urls.append(clean_url)
                    except:
                        continue
                
                print(f"✅ 페이지 {page}: {len(page_urls)}개 새 링크 발견")
                
                if page < max_pages:
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, 'a.pageNav-jump--next')
                        next_button.click()
                        time.sleep(2)
                    except NoSuchElementException:
                        print("⚠️ 다음 페이지 없음")
                        break
                        
            except Exception as e:
                print(f"❌ 페이지 {page} 처리 중 오류: {e}")
                break
        
        print(f"\n✅ 총 {len(self.collected_urls)}개 링크 수집 완료")
        
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
            print(f"❌ 본문 추출 실패 ({url}): {e}")
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
        """구글 시트에 저장"""
        if not self.results:
            print("⚠️ 저장할 데이터가 없습니다.")
            return
        
        print(f"\n💾 구글 시트에 {len(self.results)}개 데이터 저장 중...")
        
        try:
            existing_rows = len(self.sheet.get_all_values())
            
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            rows = []
            
            for result in self.results:
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
                
                print(f"✅ {len(rows)}개 데이터 저장 완료!")
                
        except Exception as e:
            print(f"❌ 구글 시트 저장 실패: {e}")
    
    def run(self, keyword, max_pages=5, max_threads=50):
        """메인 실행"""
        print("=" * 60)
        print("🚀 Purse Forum 크롤러 시작")
        print("=" * 60)
        
        try:
            self.search_forum(keyword)
            self.collect_thread_links(max_pages)
            
            print(f"\n📖 본문 수집 시작... (최대 {max_threads}개)")
            
            urls_to_process = list(self.collected_urls)[:max_threads]
            
            for i, url in enumerate(urls_to_process, 1):
                print(f"\n[{i}/{len(urls_to_process)}] {url}")
                
                result = self.extract_thread_content(url)
                
                if result:
                    self.results.append(result)
                    print(f"✅ 수집 완료: {result['title'][:50]}...")
                
                if i < len(urls_to_process):
                    time.sleep(DELAY_BETWEEN_REQUESTS)
            
            self.save_to_sheet()
            
            print("\n" + "=" * 60)
            print("✅ 크롤링 완료!")
            print(f"📊 총 수집: {len(self.results)}개")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            self.driver.quit()
            print("🔒 브라우저 종료")

if __name__ == "__main__":
    scraper = PurseForumScraper()
    scraper.run(
        keyword=SEARCH_KEYWORD,
        max_pages=MAX_PAGES,
        max_threads=MAX_THREADS
    )