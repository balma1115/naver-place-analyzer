import asyncio
from playwright.async_api import async_playwright, TimeoutError
from typing import List, Dict, Any

# ==============================================================================
# SECTION 1: 플레이스 정보 분석 (Place Information Scraper)
# ==============================================================================

# --- Helper functions for concurrent scraping ---

async def get_text_or_default(frame, selector, default="정보 없음"):
    """Helper to safely get inner text from a selector within a frame."""
    try:
        await frame.wait_for_selector(selector, state='attached', timeout=2000)
        return await frame.locator(selector).first.inner_text(timeout=1000)
    except TimeoutError:
        return default

async def get_text_from_locator(locator, selector, default="정보 없음"):
    """Helper to safely get inner text from a child of a locator."""
    try:
        return await locator.locator(selector).first.inner_text(timeout=1000)
    except (TimeoutError, AttributeError):
        return default

async def get_attribute_or_default(frame, selector, attribute, default="정보 없음"):
    """Helper to safely get an attribute from a selector."""
    try:
        await frame.wait_for_selector(selector, state='attached', timeout=2000)
        return await frame.locator(selector).first.get_attribute(attribute, timeout=1000)
    except TimeoutError:
        return default

async def get_coupon_status(frame, selector, default="쿠폰 없음"):
    """Helper to check for the existence of a coupon element."""
    try:
        await frame.wait_for_selector(selector, state='visible', timeout=2000)
        return "쿠폰 있음"
    except TimeoutError:
        return default

async def get_directions(frame, more_button_selector, directions_selector, default="정보 없음"):
    """Helper to get directions, attempting to click 'more' button."""
    try:
        more_button = frame.locator(more_button_selector).first
        if await more_button.is_visible():
            await more_button.click(timeout=1000)
            await frame.page.wait_for_timeout(300)
        return await frame.locator(directions_selector).first.inner_text(timeout=1000)
    except (TimeoutError, AttributeError):
        return default

async def get_list_items_as_text(frame, list_selector, default="정보 없음"):
    """Helper to get all items from a list and join them as text."""
    try:
        await frame.wait_for_selector(list_selector, state='attached', timeout=3000)
        items = await frame.locator(list_selector).all()
        if not items: return default
        texts = await asyncio.gather(*(item.inner_text() for item in items))
        return "\n".join(texts)
    except TimeoutError:
        return default

async def get_facilities(frame, container_selector, default="정보 없음"):
    """Helper to get a comma-separated list of facilities."""
    try:
        await frame.wait_for_selector(container_selector, state='visible', timeout=3000)
        items = await frame.locator(f"{container_selector} span").all()
        if not items: return default
        texts = await asyncio.gather(*(item.inner_text() for item in items))
        return ", ".join(filter(None, texts))
    except TimeoutError:
        return default

async def get_image_urls(frame, container_selector, default=[]):
    """Helper to get all image source URLs."""
    try:
        await frame.wait_for_selector(container_selector, state='visible', timeout=3000)
        elements = await frame.locator(f"{container_selector} img").all()
        if not elements: return default
        urls = await asyncio.gather(*(img.get_attribute('src') for img in elements))
        return [url for url in urls if url]
    except TimeoutError:
        return default

async def get_menu_names(frame, container_selector, default="메뉴 정보 없음"):
    """Helper to get all menu names from the main tab."""
    try:
        await frame.wait_for_selector(container_selector, state='visible', timeout=3000)
        items = await frame.locator(f"{container_selector} a > span").all()
        if not items: return default
        texts = await asyncio.gather(*(item.inner_text() for item in items))
        return ", ".join(filter(None, texts))
    except TimeoutError:
        return default

async def get_action_tabs(frame, container_selector, default="탭 정보 없음"):
    """Helper to get all action tab names."""
    try:
        await frame.wait_for_selector(container_selector, state='visible', timeout=3000)
        items = await frame.locator(f"{container_selector} a, {container_selector} button").all()
        if not items: return default
        texts = await asyncio.gather(*(item.inner_text() for item in items))
        return ", ".join(filter(None, texts))
    except TimeoutError:
        return default

async def get_news_data(frame, default="소식 정보 없음"):
    """Clicks the 'news' tab and scrapes the latest news articles."""
    try:
        await frame.locator("div.place_fixed_maintab a:has-text('소식')").first.click()
        await frame.page.wait_for_timeout(1000)

        news_container_selector = "#app-root > div > div > div:nth-child(7) > div > div.place_section.no_margin > div > ul"
        await frame.wait_for_selector(news_container_selector, state='visible', timeout=5000)

        articles = await frame.locator(f"{news_container_selector} > li").all()
        if not articles: return default

        news_results = []
        for article in articles[:3]: # 최신 3개만
            author = await get_text_from_locator(article, ".pui__hvyFHZ > div > span > span", "작성자 정보 없음")
            title = await get_text_from_locator(article, ".pui__dGLDWy", "제목 없음")
            content = await get_text_from_locator(article, ".pui__vn15t2 > a", "내용 없음")
            date = await get_text_from_locator(article, ".pui__QztK4Q .O8Q6I span", "날짜 정보 없음")
            news_results.append({"author": author, "title": title, "content": content, "date": date})
        return news_results
    except (TimeoutError, AttributeError):
        return default

async def get_review_data(frame, default={"visitor_reviews": [], "blog_reviews": []}):
    """Clicks the 'review' tab and scrapes detailed visitor and blog reviews."""
    try:
        await frame.locator("div.place_fixed_maintab a:has-text('리뷰')").first.click()
        await frame.page.wait_for_timeout(1500)
        
        visitor_reviews, blog_reviews = [], []

        # --- Scrape Visitor Reviews ---
        try:
            await frame.locator("#_subtab_view a:has-text('방문자')").first.click()
            await frame.page.wait_for_timeout(1000)
            review_list_selector = "#_review_list"
            await frame.wait_for_selector(review_list_selector, state='visible', timeout=5000)
            
            review_items = await frame.locator(f"{review_list_selector} > li").all()
            for item in review_items[:3]: # 최신 3개
                nickname = await get_text_from_locator(item, "a.pui__hvyFHZ", "정보 없음")
                content = await get_text_from_locator(item, "div.pui__vn15t2 > a:nth-child(1)", "내용 없음")
                date = await get_text_from_locator(item, "div.pui__QztK4Q > div.Vk05k > div > span:nth-child(1)", "정보 없음")
                reply_content = await get_text_from_locator(item, "div.pui__GbW8H7 div.pui__J0tczd > a:nth-child(1)", "답변 없음")
                visitor_reviews.append({"nickname": nickname, "content": content, "date": date, "reply": reply_content})
        except (TimeoutError, AttributeError):
            pass

        # --- Scrape Blog Reviews ---
        try:
            await frame.locator("#_subtab_view > div > a:nth-child(2)").click()
            await frame.page.wait_for_timeout(1000)
            blog_container_selector = "#app-root > div > div > div:nth-child(7) > div:nth-child(3) > div > div.place_section_content > ul"
            await frame.wait_for_selector(blog_container_selector, state='visible', timeout=5000)
            blog_items = await frame.locator(f"{blog_container_selector} > li").all()
            for item in blog_items[:3]: # 최신 3개
                author = await get_text_from_locator(item, "span.pui__hvyFHZ.pui__vB0YTs > div.pui__JiVbY3 > span > span", "정보 없음")
                title = await get_text_from_locator(item, "div.pui__dGLDWy", "제목 없음")
                summary = await get_text_from_locator(item, "div.pui__vn15t2 > span", "요약 없음")
                date = await get_text_from_locator(item, "div.u5XwJ > span > span", "정보 없음")
                blog_reviews.append({"author": author, "title": title, "summary": summary, "date": date})
        except (TimeoutError, AttributeError):
            pass

        return {"visitor_reviews": visitor_reviews, "blog_reviews": blog_reviews}
    except (TimeoutError, AttributeError):
        return default

# --- Main Scraper Function for Place Analysis ---

async def run_place_analysis(url: str) -> Dict[str, Any]:
    """
    주어진 네이버 지도 URL에서 업체 정보를 스크래핑하여 딕셔너리로 반환합니다.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        scraped_data = {}
        try:
            await page.goto(url, wait_until="load", timeout=90000)
            entry_iframe = await page.wait_for_selector("#entryIframe", timeout=15000)
            frame = await entry_iframe.content_frame()
            await frame.wait_for_selector("#_title", timeout=30000)

            # 기본 정보 병렬 스크래핑
            place_name_task = get_text_or_default(frame, "#_title > div > span.GHAhO")
            category_task = get_text_or_default(frame, "#_title > div > span.lnJFt")
            place_name, category = await asyncio.gather(place_name_task, category_task)
            
            scraped_data['name'] = place_name
            scraped_data['category'] = category

            main_content_selector = "#app-root > div > div > div:nth-child(6)"
            tasks = {
                "address": get_text_or_default(frame, f"{main_content_selector} .LDgIH"),
                "phone": get_text_or_default(frame, f"{main_content_selector} .xlx7Q"),
                "coupon": get_coupon_status(frame, f"{main_content_selector} .l__qc"),
                "directions": get_directions(frame, f"{main_content_selector} .AZ9_F .rvCSr", f"{main_content_selector} .AZ9_F .zPfVt"),
                "price_info": get_list_items_as_text(frame, f"{main_content_selector} .tXI2c li"),
                "facilities": get_facilities(frame, f"{main_content_selector} .Uv6Eo"),
                "blog_link": get_attribute_or_default(frame, f"{main_content_selector} .yIPfO .jO09N > a", 'href'),
                "instagram_link": get_attribute_or_default(frame, f"{main_content_selector} .yIPfO .Cycl8 a", 'href'),
                "images": get_image_urls(frame, "#app-root > div > div > div.CB8aP"),
            }
            results = await asyncio.gather(*tasks.values())
            scraped_data.update(zip(tasks.keys(), results))

            # 순차적 탭 정보 스크래핑
            scraped_data["news"] = await get_news_data(frame)
            scraped_data["reviews"] = await get_review_data(frame)

        except Exception as e:
            print(f"플레이스 분석 스크래핑 오류: {e}")
            raise e
        finally:
            await browser.close()
        
        return scraped_data

# ==============================================================================
# SECTION 2: 키워드 순위 확인 (Keyword Rank Checker)
# ==============================================================================

async def search_and_check_ranking(page, keyword, target_business, max_pages=5):
    """특정 키워드로 검색하고 목표 업체의 순위를 확인"""
    print(f"\n🔍 '{keyword}' 키워드로 검색 시작...")
    try:
        await page.goto("https://map.naver.com/p?c=12.11,0,0,0,dh", wait_until="load", timeout=30000)
        search_input_selector = "#home_search_input_box > div > div > div"
        await page.wait_for_selector(search_input_selector, timeout=15000)
        await page.click(search_input_selector)
        
        await page.keyboard.press("Control+A")
        await page.keyboard.press("Delete")
        await page.keyboard.type(keyword)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(5000)

        if "search" not in page.url:
            print(f"❌ '{keyword}' 검색이 제대로 실행되지 않음")
            return {'keyword': keyword, 'rank': None, 'error': 'Search not executed properly'}
        
        current_page = 1
        found_target = False
        target_rank = None
        
        while current_page <= max_pages and not found_target:
            print(f"📄 {current_page}페이지 확인 중...")
            try:
                search_iframe = await page.wait_for_selector("#searchIframe", timeout=5000)
                iframe = await search_iframe.content_frame()
                await iframe.wait_for_selector("#_pcmap_list_scroll_container", timeout=5000)
                
                # 스크롤 다운
                for _ in range(5):
                    await iframe.evaluate("document.querySelector('#_pcmap_list_scroll_container').scrollTop = document.querySelector('#_pcmap_list_scroll_container').scrollHeight")
                    await page.wait_for_timeout(1000)

                li_elements = await iframe.query_selector_all("#_pcmap_list_scroll_container ul li")
                
                for i, element in enumerate(li_elements, 1):
                    try:
                        name_element = await element.query_selector("span.YwYLL")
                        business_name = await name_element.inner_text() if name_element else ""
                        
                        if business_name:
                            global_rank = (current_page - 1) * 50 + i # 페이지당 50개 가정
                            if target_business in business_name:
                                found_target = True
                                target_rank = global_rank
                                print(f"🎯 목표 업체 발견! '{target_business}' → {global_rank}위")
                                break
                    except Exception as e:
                        print(f"순위 추출 중 작은 오류: {e}")
                
                if found_target: break

                # 다음 페이지로 이동
                pagination_selector = "#app-root > div > div.XUrfU > div.zRM9F > a:nth-child(6)"
                next_button = await page.wait_for_selector(pagination_selector, timeout=3000)
                if await next_button.get_attribute("aria-disabled") != "true":
                    await next_button.click()
                    await page.wait_for_timeout(3000)
                    current_page += 1
                else:
                    break # 마지막 페이지
            except TimeoutError:
                print(f"❌ {current_page}페이지 로딩 또는 다음 페이지 버튼 찾기 실패")
                break
        
        return {'keyword': keyword, 'rank': target_rank if found_target else '50위 초과 또는 없음'}

    except Exception as e:
        print(f"❌ '{keyword}' 검색 중 오류 발생: {e}")
        return {'keyword': keyword, 'rank': None, 'error': str(e)}

# --- Main Function for Keyword Ranking ---

async def run_keyword_ranking_check(target_business: str, keywords: List[str]) -> List[Dict[str, Any]]:
    """
    여러 키워드에 대해 목표 업체의 순위를 확인하여 리스트로 반환합니다.
    """
    all_results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
        )
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        try:
            for keyword in keywords:
                result = await search_and_check_ranking(page, keyword, target_business, max_pages=3)
                all_results.append(result)
                if keywords.index(keyword) < len(keywords) - 1:
                    await page.wait_for_timeout(2000)
        except Exception as e:
            print(f"키워드 순위 확인 중 전체 오류: {e}")
            raise e
        finally:
            await browser.close()
            
    return all_results