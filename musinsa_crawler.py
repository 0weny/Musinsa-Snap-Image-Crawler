!pip install selenium

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import os
from urllib.parse import urljoin


def download_image(img_url, folder, filename):
    """이미지를 다운로드하는 함수"""
    try:
        response = requests.get(img_url, timeout=10)
        if response.status_code == 200:
            filepath = os.path.join(folder, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"다운로드 완료: {filename}")
            return True
    except Exception as e:
        print(f"다운로드 실패 {filename}: {e}")
    return False


def crawl_musinsa_snaps(url, scroll_count=10):
    """무신사 스냅 크롤링 함수 (5000개 제한 로직 추가)"""

    # --- 추가된 상수 ---
    MAX_IMAGES = 5000  # 크롤링 최대 이미지 개수 제한
    # ------------------

    # 저장 폴더 생성
    save_folder = "classic"
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # Chrome 옵션 설정
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 헤드리스 모드 (브라우저 창 안 띄움)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    # 드라이버 시작
    driver = webdriver.Chrome(options=options)

    try:
        print(f"페이지 접속 중: {url}")
        driver.get(url)

        # 페이지 로드 대기
        time.sleep(3)

        # 이미지 URL을 저장할 set (중복 방지)
        image_urls = set()

        # 스크롤 루프
        for i in range(scroll_count):
            print(f"\n스크롤 {i + 1}/{scroll_count}")

            # 현재 페이지의 이미지 찾기
            img_elements = driver.find_elements(By.TAG_NAME, "img")

            for img in img_elements:
                try:
                    src = img.get_attribute('src')
                    # 실제 스냅 이미지만 필터링 (로고나 아이콘 제외)
                    if src and ('snap' in src.lower() or 'image' in src.lower()):
                        if src.startswith('http'):
                            image_urls.add(src)
                except:
                    continue

            print(f"현재까지 발견된 이미지: {len(image_urls)}개")

            # --- 핵심 수정 부분: 5000개 제한 검사 및 중단 ---
            if len(image_urls) >= MAX_IMAGES:
                print(f"🚨 발견된 이미지 {len(image_urls)}개가 목표 개수 {MAX_IMAGES}개를 초과했습니다. 크롤링을 중단합니다.")
                break
            # --------------------------------------------------

            # 스크롤 다운
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # 새 이미지 로드 대기


        print(f"\n총 {len(image_urls)}개의 이미지 발견")

        # 다운로드할 URL 리스트를 최대치로 슬라이싱 (5000개 제한)
        urls_to_download = list(image_urls)[:MAX_IMAGES]

        # 이미지 다운로드
        print("\n이미지 다운로드 시작...")
        downloaded = 0
        for idx, img_url in enumerate(urls_to_download, 1):
            filename = f"classic_{idx:04d}.jpg"
            if download_image(img_url, save_folder, filename):
                downloaded += 1

        print(f"\n✅ 완료! {downloaded}개의 이미지가 '{save_folder}' 폴더에 저장되었습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    finally:
        driver.quit()


# 실행
if __name__ == "__main__":
    # Classic(styles=9), Romantic(styles=12), 성별필터(gf=A)가 모두 적용된 URL
    url = "https://www.musinsa.com/snap/main/recommend?styles=9&styles=12&gf=A"

    print(f"\n==========================================")
    print(f"[Classic & Romantic] 통합 크롤링 시작")
    print(f"URL: {url}")
    print(f"==========================================")

    # scroll_count는 충분히 높은 횟수를 유지하여 5000개에 도달할 때까지 스크롤 시도
    crawl_musinsa_snaps(url, scroll_count=3000)



#----------------------------------------------
import shutil
import os
from google.colab import files

# 압축할 폴더 이름
folder_to_zip = "casual"
# 압축 파일 이름
zip_filename = f"{folder_to_zip}.zip"

# 폴더가 존재하는지 확인
if os.path.exists(folder_to_zip):
    # 폴더를 zip 파일로 압축
    shutil.make_archive(folder_to_zip, 'zip', folder_to_zip)
    print(f"'{folder_to_zip}' 폴더가 '{zip_filename}'으로 압축되었습니다.")

    # Colab에서 파일 다운로드 링크 제공
    try:
        files.download(zip_filename)
        print(f"'{zip_filename}' 파일 다운로드를 시작합니다.")
    except Exception as e:
        print(f"파일 다운로드 중 오류 발생: {e}")
else:
    print(f"'{folder_to_zip}' 폴더를 찾을 수 없습니다.")
