# MD Allboard

MD Allboard는 MD 업무 데이터를 빠르게 업로드하고, 상품·매장·스케줄·플랜을 분석하기 위한 Streamlit 기반 대시보드입니다.

ERP 또는 엑셀 데이터를 업로드하면 상품 카테고리 분석, 매장 진도율 분석, 보고용 Summary Report, 16:9 이미지 리포트 다운로드까지 사용할 수 있습니다.

---

## 1. 주요 기능

### Product Dashboard

상품 카테고리별 판매 현황을 분석하는 페이지입니다.

* CATE1 / CATE2 / CATE3 기준 분석
* 판매금액 / 판매수량 확인
* 상품별 BEST / WORST 확인
* 입고수량, 판매율, 할인율, 재고수량 확인
* 상품 분석 리포트 엑셀 다운로드

---

### Store Dashboard

매장별 목표 대비 진도율을 분석하는 페이지입니다.

* 일간 / 주간 / 월간 기준 전환
* 지역별 목표 대비 진도율 확인
* 매장별 목표 / 매출 / 차이금액 확인
* 방문객수, 구매건수, 전환율, 객단가 확인
* 우수 매장 / 위험 매장 확인

---

### Product Summary Report

상품 데이터를 보고용 한 장 요약 형태로 정리하는 페이지입니다.

* 총 판매금액 / 판매수량 / 상품 수 확인
* TOP 상품 / LOW 상품 요약
* MD 자동 코멘트 생성
* Summary Report 엑셀 다운로드
* 16:9 보고용 PNG 이미지 다운로드

---

### Store Summary Report

매장 데이터를 보고용 한 장 요약 형태로 정리하는 페이지입니다.

* 총 목표 / 총 매출 / 평균 진도율 확인
* BEST 매장 / LOW 매장 요약
* 지역별 / 매장별 흐름 확인
* Store 자동 코멘트 생성
* Store Summary 엑셀 다운로드
* 16:9 보고용 PNG 이미지 다운로드

---

### MD Plan Builder

연간 MD 계획과 시즌 운영 계획을 구성하는 페이지입니다.

* 연간 목표 구조 설계
* 월별 / 시즌별 계획 구성
* DROP 운영 계획 정리
* 상품 운영 방향 검토

---

### MD Schedule

시즌 일정과 상품 준비 일정을 관리하는 페이지입니다.

* 시즌별 주요 일정 확인
* DROP 일정 관리
* 기획 / 생산 / 입고 / 판매 일정 흐름 확인
* MD 업무 스케줄 정리

---

## 2. 배포 주소

Streamlit Cloud 배포 주소:

https://md-allboard.streamlit.app/

---

## 3. 로컬 실행 방법

터미널에서 프로젝트 폴더로 이동합니다.

```bash
cd C:\Users\andy3\MD_Dashboard
```

Streamlit 앱을 실행합니다.

```bash
streamlit run app.py
```

정상 실행되면 브라우저에서 아래 주소로 접속됩니다.

```text
http://localhost:8501
```

---

## 4. 프로젝트 구조

```text
MD_Dashboard/
├─ app.py
├─ README.md
├─ requirements.txt
├─ packages.txt
├─ .gitignore
├─ .streamlit/
├─ data/
│  ├─ sample/
│  ├─ raw/
│  └─ uploaded/
└─ pages/
   ├─ 1_MD_Schedule.py
   ├─ 2_Product_Dashboard.py
   ├─ 3_Store_Dashboard.py
   ├─ 4_MD_Plan_Builder.py
   ├─ 5_Product_Summary_Report.py
   └─ 6_Store_Summary_Report.py
```

---

## 5. 업로드 데이터 구조

### 상품 데이터 필수 컬럼

Product Dashboard와 Product Summary Report에서 사용합니다.

```text
일자
CATE1
CATE2
CATE3
상품명
TAG가
입고수량
판매수량
판매금액
할인율
```

선택 컬럼:

```text
실판매가
상품코드
```

---

### 매장 데이터 필수 컬럼

Store Dashboard와 Store Summary Report에서 사용합니다.

```text
일자
지역
매장
일목표
일매출
방문객수
구매건수
```

선택 컬럼:

```text
객단가
```

---

## 6. 데이터 보안 기준

이 프로젝트에서는 코드와 샘플 데이터만 GitHub에 올립니다.

실제 회사 데이터는 GitHub에 올리지 않습니다.

### GitHub에 올려도 되는 것

```text
코드
샘플 데이터
README
requirements.txt
packages.txt
```

### GitHub에 올리면 안 되는 것

```text
실제 ERP 데이터
실제 매출 데이터
실제 재고 데이터
거래처 정보
원가 / 마진 자료
```

현재 업로드 방식은 사용자별 세션에서 파일을 읽어 분석하는 구조입니다.

* 업로드 파일은 GitHub에 저장되지 않습니다.
* 업로드 파일은 다른 사용자에게 자동 공유되지 않습니다.
* 각 사용자는 본인이 업로드한 파일 기준으로만 분석 화면을 확인합니다.

---

## 7. GitHub 배포 방법

수정 후 상태를 확인합니다.

```bash
git status
```

변경사항을 추가합니다.

```bash
git add .
```

커밋합니다.

```bash
git commit -m "수정 내용 입력"
```

GitHub에 업로드합니다.

```bash
git push
```

마지막으로 상태를 확인합니다.

```bash
git status
```

아래처럼 나오면 정상입니다.

```text
nothing to commit, working tree clean
```

---

## 8. Streamlit Cloud 배포 구조

이 프로젝트는 GitHub 저장소와 Streamlit Cloud가 연결되어 있습니다.

작업 흐름은 다음과 같습니다.

```text
로컬 코드 수정
→ localhost에서 테스트
→ GitHub push
→ Streamlit Cloud 자동 배포
→ 배포 주소에서 확인
```

로컬 주소:

```text
http://localhost:8501
```

배포 주소:

```text
https://md-allboard.streamlit.app/
```

---

## 9. 설치 패키지

Python 패키지는 `requirements.txt`에서 관리합니다.

예시:

```text
streamlit
pandas
numpy
plotly
openpyxl
pillow
```

Linux 시스템 패키지는 `packages.txt`에서 관리합니다.

현재 한글 이미지 다운로드를 위해 아래 패키지를 사용합니다.

```text
fonts-noto-cjk
```

---

## 10. 현재 개발 상태

완료된 기능:

* 멀티페이지 구조 정리
* 상품 대시보드 업로드 기능
* 매장 대시보드 업로드 기능
* 업로드 양식 다운로드
* 업로드 데이터 미리보기
* 상품 분석 리포트 엑셀 다운로드
* Product Summary Report 생성
* Store Summary Report 생성
* 16:9 보고용 PNG 이미지 다운로드
* 배포 환경 한글 폰트 설정
* Streamlit Cloud 배포

---

## 11. 향후 고도화 후보

* 실제 ERP 컬럼명 자동 변환
* 업로드 오류 메시지 개선
* 상품/매장 데이터 한 번 업로드 후 여러 페이지에서 공유
* 관리자 업로드 방식 도입
* 사내 서버 또는 ERP 직접 연결
* 자동 리포트 발송
* 공통 함수 utils 분리
* 코드 구조 정리 및 유지보수 개선

---

## 12. 프로젝트 목적

이 프로젝트의 목적은 MD 업무에서 반복되는 엑셀 분석과 보고서 작성을 자동화하는 것입니다.

최종적으로는 ERP 또는 엑셀 데이터를 기반으로 매장, 상품, 시즌, 플랜 데이터를 빠르게 분석하고, 보고용 리포트까지 자동 생성하는 실무형 MD 대시보드로 발전시키는 것을 목표로 합니다.
