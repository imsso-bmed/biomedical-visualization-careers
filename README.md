# BioMedical Visualization Careers

의료미술·과학 시각화·WebGL 개발 관련 국내외 채용, 외주, 공모, 지원금, 학회 정보를 탐색하는 한국어 정적 사이트입니다.

## GitHub Pages 배포

1. ZIP을 풀고 숨김 파일과 `.github/workflows/update.yml`을 포함해 대상 저장소의 `main` 루트에 커밋합니다.
2. 저장소의 **Settings → Pages → Build and deployment → Source**에서 **GitHub Actions**를 선택합니다.
3. **Actions → Collect jobs and deploy GitHub Pages → Run workflow**를 실행합니다. 첫 push가 Pages 설정 전에 실행됐다면 설정 후 수동 실행합니다.
4. 실행 로그에서 수집 결과와 deploy 단계의 성공 여부를 확인한 뒤 [공개 페이지](https://imsso-bmed.github.io/biomedical-visualization-careers/)에서 확인합니다.

워크플로는 매일 **09:17 KST**에 예약되어 있습니다. GitHub Actions의 스케줄 처리 시간에 따라 실행이 지연될 수 있습니다. 수집 후 공고 이력을 커밋하고 같은 실행에서 Pages에 배포합니다. 저장소 정책에서 워크플로의 데이터 커밋과 공식 Pages 액션이 허용되어야 합니다.

## 데이터 운영

- `config/sources.json`의 Greenhouse와 Lever 항목은 공식 공개 API의 GET 요청으로 수집합니다. 등록 보드는 Figma와 Kitware입니다. `manual`은 채용 원문에서 직접 확인할 기업 링크입니다.
- 채용 카드는 정규화한 공고 URL로 중복을 제거합니다. 정상 조회된 보드에서 게시물이 사라지면 마감으로 기록합니다. 일부 조회가 실패하면 해당 공고를 확인 필요로 변경하고 마지막 검증일을 보존합니다. 모든 보드가 실패하면 이전 스냅샷을 유지하고 워크플로 로그에 경고를 남깁니다.
- 근무 방식은 ATS가 명시한 경우에 표시합니다. 한국 거주 상태로 근무할 수 있는지와 비자 지원은 각각 확인 필요로 둡니다. 원격 표시는 한국에서 원격 근무할 수 있다거나 비자를 지원한다는 뜻이 아닙니다.
- `data/jobs.json`은 공식 채용 보드에서 조회한 실제 공고의 최근 스냅샷입니다. `data/opportunities.json`과 `data/events.json`은 주최자 공지에 근거해 수동 갱신합니다.
- 관심 목록은 브라우저에 저장됩니다. 뉴스레터 영역은 구독 서비스 연동 전 준비 중 상태로 표시됩니다.
- 단체 디렉터리는 `index.html`에서 관리합니다. 기존 목록 중 공식 링크 근거가 불명확한 항목은 확인 필요로 표시합니다.

## 로컬 확인

```sh
python3 scripts/validate.py
node --check app.js
python3 -m http.server 8000
```

브라우저에서 `http://localhost:8000/`을 엽니다. 공개 API 연결이 가능한 환경에서는 `python3 scripts/collect.py`로 수집을 직접 실행할 수 있습니다.
