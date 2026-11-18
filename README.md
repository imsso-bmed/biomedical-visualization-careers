# BioMedical Visualization Careers

한국인 이용자를 위한 의료·과학 시각화 채용·외주·학회·공모 플랫폼의 GitHub Pages MVP입니다.

## 배포
1. GitHub에서 `biomedical-visualization-careers` **공개 저장소**를 생성합니다.
2. 이 폴더의 모든 파일을 저장소 기본 브랜치에 올립니다.
3. **Settings → Pages → Build and deployment → Deploy from a branch → main / (root)**를 선택합니다.
4. 공개 주소: `https://<사용자명>.github.io/biomedical-visualization-careers/` (설정 후 실제 확인 필요).
5. **Actions → Update public opportunities → Run workflow**로 최초 수집을 실행합니다.

## 자동 수집 설정
`config/sources.json`에 Greenhouse/Lever를 사용하는 **실제 기업의 공개 board token**을 등록하세요. 예:
```json
{"greenhouse":[{"token":"ACTUAL_BOARD_TOKEN","name":"기업명"}],"lever":[]}
```
예시는 placeholder입니다. 현재 소스 목록은 비어 있어 자동 수집 공고는 0건입니다. 등록된 소스의 공개 API에서 관련 키워드가 포함된 공고만 수집합니다. 매일 09:17 KST 무렵 GitHub Actions가 갱신합니다(실행 지연 가능).

## 데이터와 제한
- `data/jobs.json`: API 수집 채용공고. 분류와 고용형태는 확정되지 않으면 `확인 필요`로 표시합니다.
- `data/opportunities.json`, `data/events.json`: 초기 빈 배열이며 수동 검수·추가 수집기 구현 필요.
- 학회 커뮤니티 링크는 초기 HTML에 포함되어 있으므로 정기 검증을 추가하는 것이 좋습니다.
- 뉴스레터는 아직 미연동이며 이메일은 저장되지 않습니다.
- API 오류 시 과거 데이터를 보존하며 검증 상태를 표시합니다. 공고 마감 자동 판정은 아직 구현하지 않았습니다.
- 타사 사이트의 수집 정책과 API 약관을 준수해야 합니다.
