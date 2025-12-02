def search_forum(self, keyword):
    """포럼 섹션 접속"""
    print(f"\n🔍 Asian Plastic Surgery 포럼 접속 중...")
    
    # 직접 포럼 섹션으로 이동
    forum_url = "https://forum.purseblog.com/forums/asian-plastic-surgery-cosmetic-procedures.277/"
    
    self.driver.get(forum_url)
    time.sleep(3)
    
    print(f"📄 페이지 로드 완료: {self.driver.current_url}")
    print(f"🔍 키워드 '{keyword}' 필터링은 본문 수집 시 적용됩니다")

def collect_thread_links(self, max_pages=5, keyword=None):
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
                            # 키워드 필터링 (제목에 키워드 포함된 것만)
                            if keyword:
                                title = link.text.lower()
                                if keyword.lower() in title:
                                    self.collected_urls.add(clean_url)
                                    page_urls.append(clean_url)
                            else:
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

def run(self, keyword, max_pages=5, max_threads=50):
    """메인 실행"""
    print("=" * 60)
    print("🚀 Purse Forum 크롤러 시작")
    print("=" * 60)
    
    try:
        self.search_forum(keyword)
        self.collect_thread_links(max_pages, keyword)
        
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