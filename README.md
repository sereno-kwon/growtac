# GROWTAC | Rubi Workshop

growtac.rubiworkshop.com 원페이지 정적 사이트. gokiso.rubiworkshop.com과 같은 구조입니다.

- `index.html` 원페이지 본체 (한국어), `en/index.html` 영어, `ja/index.html` 일본어. 모두 빌드 결과물입니다.
- 원페이지 구성 (GROWTAC · EQUAL BRAKE(+ 시스템 구조, 플랫/포스트, 컬러) · KASHIMA COAT · CONTROL LEVER · SHOWROOM)
- `index.src.html` 편집용 원본. 스펙 표는 `{{SPEC_*}}` 자리에 `build.py`가 채웁니다. 내용을 고칠 때는 `index.src.html`을 수정한 뒤 `python3 build.py`를 실행합니다. `index.html`을 직접 고치면 다음 빌드 때 덮어써집니다.
- `build.py` 스펙 데이터(브레이크, 카시마 코트, 컨트롤 레버)와 빌드 스크립트. `python3 build.py`로 세 언어 페이지를 한 번에 생성, `python3 build.py --preview`는 이미지를 원본 주소로 연결한 preview*.html 생성
- `i18n/en.json`, `i18n/ja.json` 번역. `strings`는 "한국어 원문": "번역" 쌍이라, 한국어 문장을 고치면 두 파일의 같은 키도 함께 고칩니다. 빠진 번역은 빌드 때 목록으로 출력됩니다.
- `404.html` 하위 주소(/brake, /kashima, /lever, /en/lever, /ja/brake, /dealer 등)를 섹션으로 연결
- `images/` 섹션별 이미지 (`hero`, `brand`, `brake`, `tech`, `color`, `kashima`, `lever`, `showroom`)
- `.github/image-manifest.txt` + `fetch-images.yml` 그로우택 공식 사이트(growtac.com)와 루비서플라이 CDN(cdn.imweb.me) 이미지 이전용 워크플로

## 이미지
매니페스트를 수정해 main에 푸시하면 Actions가 이미지를 받아 `images/`에 커밋합니다.
이미 받은 파일은 건너뛰므로, 이미지를 교체할 때는 해당 파일을 지우거나 새 파일명으로 추가합니다.
첫 세팅 때는 Actions 탭에서 `Fetch images from Growtac / Rubi CDN`을 한 번 실행(Run workflow)하면 됩니다.
`images/logo.png`는 그로우택 공식 흰색 로고이며, 헤더에서 CSS 필터로 검게 반전해 씁니다.
루비워크샵에서 직접 촬영한 장착 사진(rubi-growtac-lifestyle-*)을 `images/hero/`, `images/brake/`에 추가하면 페이지가 훨씬 살아납니다.

## 상품 링크
루비워크샵(rubiworkshop.com)에 그로우택 카테고리가 아직 없어, 상품 버튼은 루비서플라이(rubisupply.com/growtac, /growtac-brakes, /growtac-lever)로, 상담 버튼은 rubiworkshop.com/models로 연결합니다. 루비워크샵에 카테고리가 생기면 `index.src.html`의 링크만 바꾸고 다시 빌드합니다.

## 배포 · 도메인
`CNAME`은 growtac.rubiworkshop.com. GitHub Pages로 배포할 때는 rubiworkshop.com DNS에 `growtac` CNAME 레코드 → `sereno-kwon.github.io`를 추가하고, 저장소 Settings → Pages에서 Custom domain에 같은 주소를 넣고 Enforce HTTPS를 켭니다.
Cloudflare Pages로 배포할 때는 이 저장소를 연결하고(빌드 명령 없음, 출력 디렉터리 `/`), Custom domain에 growtac.rubiworkshop.com을 추가한 뒤 안내되는 CNAME 레코드를 DNS에 넣습니다.
