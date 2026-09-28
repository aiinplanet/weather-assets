# 매일 '오늘의 날씨' 기사 → FAM타임스 전송 절차

이 저장소는 FAM타임스 날씨 기사용 영상·대표이미지를 공개 주소로 제공하기 위한 곳이다.
팸타임스 서버는 raw.githubusercontent.com 주소에서 파일을 직접 내려받는다.

## 1. 취재 (WebSearch / WebFetch)
- 오늘(KST) 날짜의 기상청 단기·중기 예보 보도를 2~4개 이상 대조한다
  (예: "오늘 날씨 {M월 D일}", "{M월 D일} 날씨 기상청", 연합뉴스·뉴스1·뉴시스 등 날씨 기사).
- 확인할 항목: 전국 하늘 상태, 강수 지역·시점·예상 강수량, 아침 최저·낮 최고 범위,
  9개 도시(서울 인천 대전 대구 광주 울산 부산 창원 제주, 창원 대신 다른 도시만 확인되면 그 도시) 기온,
  미세먼지, 물결, 특보(폭염·한파·호우·강풍 등), 앞으로 3~6일 기온 흐름.
- 확인되지 않은 수치는 쓰지 않는다. 수치가 기사마다 다르면 가장 최근 발표 기준을 쓴다.

## 2. data.json 작성 (tool/example-data.json 형식 그대로)
| 키 | 내용 |
|---|---|
| datepill | "2026. 9. 28  월요일" |
| badge | "●  WEATHER BRIEF  ·  2026.09.28 MON" |
| chips | 핵심 3개 [["☂  문구", "#3fe0d8"], ["↕  문구", "#ff8a4c"], ["↓  문구", "#4fb3ff"]] (문구 짧게, 각 10자 안팎) |
| prov_order | 예시 그대로 유지 (17개 시도) |
| prov_lvl | 시도별 강수 단계 0~3 (0 비 없음). 이름은 prov_order 표기 그대로 |
| legend | [[3,"라벨"],[2,"라벨"],[1,"라벨"],[0,"비 없음"]] — 그날 강수량 구간에 맞춰 |
| callouts | [문구, 경도, 위도, 단계, 등장초(2.4~3.4)] 2~4개. 서쪽(경도<126.9)은 라벨이 왼쪽에 붙는다 |
| map_kicker / map_title / map_sub | 지도 장면 머리글. 비 없는 날은 하늘 상태·미세먼지 중심으로 |
| rain_rows | [지역, 양, 시점] 정확히 5개 (비 없는 날은 권역별 하늘 상태로 대체) |
| map_note | 미세먼지·물결 등 한 줄 (45자 이내) |
| temp_sub / temp_note | 기온 장면 부제·하단 문구 |
| cities | [도시, 최저, 최고, 아이콘] 9개. 아이콘: sun, cloudsun, cloud, rain |
| trend_title / trend_sub | 전망 장면 머리글 |
| trend | [라벨, 최저하한, 최저상한, 최고하한, 최고상한, 아이콘, 메모] 4개 |
| outro1 / outro2 | 마무리 문구 |
| source | "자료: 기상청 예보(9월 27~28일 발표) 보도 종합" 형식 |

글자가 넘치지 않는지 `WX_DATA=... WX_OUT=/tmp python3 tool/render.py still 3 8.8 16.5 21.5 25` 로
장면별 정지 화면을 만들어 Read로 눈으로 확인하고, 겹치면 문구를 줄인다.

## 3. 영상·대표이미지 공개
    sh tool/build.sh YYYY-MM-DD /path/data.json
출력된 VIDEO_URL, IMAGE_URL을 사용한다 (push 직후 몇 초 뒤 접근 가능).

## 4. FAM타임스 전송 (Famtimes 커넥터)
1. get_style_guide, list_sections 로 최신 규칙 확인.
2. upload_article_video_from_url(url=VIDEO_URL, name=영상 내용 제목, description=영상 구성 설명; "기상청 예보를 바탕으로 자체 제작한 그래픽이며 소리는 없다" 포함).
3. upload_article_image(file={download_url: IMAGE_URL, file_id: "weather-YYYY-MM-DD-thumb", file_name: "YYYY-MM-DD.jpg", mime_type: "image/jpeg"}).
4. submit_article — section "life-tips"(생활노하우), 제목 "[오늘 날씨] 핵심…핵심"(과장 없이),
   부제·요약·키워드 포함. 본문 순서:
   - 리드 <p> (누가·언제·무엇: 날짜, 전국 날씨 핵심, 기온 범위)
   - 대표이미지 <figure><img src=이미지url alt="지도 내용 설명" width="1280" height="720"><figcaption>… 기상청 예보를 바탕으로 FAM타임스가 자체 제작한 그래픽.</figcaption></figure>  ← 첫 이미지가 대표이미지가 된다
   - 둘째 <p>
   - 영상 업로드가 반환한 html의 video 태그 + 캡션 figure
   - <h3> 강수 / <h3> 기온 / <h3> 전망 / <h3> 미세먼지·생활 — 문단 2~4문장, 강수 표·도시 기온 표(<caption>)
   - style 속성·script·작성자 서명 금지.
5. 전송 결과(기사 id, 승인대기)를 보고한다. 발행은 편집국이 한다.

실패 시: 오류 내용을 그대로 보고하고, 같은 파일로 무한 재시도하지 않는다.
