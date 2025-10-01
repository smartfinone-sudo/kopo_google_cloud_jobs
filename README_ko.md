# Cloud Run Jobs 학생 실습 (Prime Counter)

이 실습은 **Cloud Run Jobs**로 간단한 배치 작업을 만들어 보고,
**여러 태스크 분할(sharding)** 과 **스케줄링(Cloud Scheduler)** 까지 경험합니다.

## 1) 예제 시나리오
- 1..N 구간을 여러 조각(shard)으로 나눠 각 태스크가 맡은 범위의 **소수(prime)** 개수를 계산합니다.
- 태스크 인덱스(`CLOUD_RUN_TASK_INDEX`)와 전체 태스크 수(`CLOUD_RUN_TASK_COUNT`)를 이용해 범위를 자동 분할합니다.
- 결과는 로그(JSON 한 줄)로 남기며, Logs Explorer에서 확인합니다.

## 2) 코드 개요
- `app/main.py`: 배치 엔트리포인트. 환경변수 `RANGE_MAX`, `PAUSE_SEC` 를 받아 동작.
- `Dockerfile`: Python 슬림 이미지 기반 컨테이너 빌드.
- `cloudbuild.yaml`: Artifact Registry로 컨테이너 빌드/푸시.
- `scripts/create_job.sh`: 잡 생성/업데이트 및 1회 실행.
- `scripts/schedule_job.sh`: 평일 21:00 KST 크론 스케줄 생성.

## 3) 준비물
- GCP 프로젝트, 빌링, Artifact Registry 리포지토리(예: `asia-northeast1` 지역의 `jobs-lab`).
- 권한: Cloud Build, Artifact Registry, Cloud Run, Cloud Scheduler.

## 4) 빌드 & 배포
```bash
gcloud config set project <PROJECT_ID>
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com cloudscheduler.googleapis.com

# Artifact Registry 리포지토리 생성(최초 1회)
gcloud artifacts repositories create jobs-lab   --repository-format=docker   --location=asia-northeast1   --description="Cloud Run Jobs student lab"

# Cloud Build로 컨테이너 빌드/푸시
gcloud builds submit   --substitutions=_REGION=asia-northeast1,_REPO=jobs-lab,_IMAGE=prime-lab
```

## 5) 잡 생성/실행
```bash
chmod +x scripts/create_job.sh
./scripts/create_job.sh <PROJECT_ID> asia-northeast1 jobs-lab prime-lab 4
# -> prime-counter 잡 생성 후 즉시 한번 실행
```

- Logs Explorer에서 `resource.type="run_job"` 또는 텍스트 `prime-counter` 로 필터링해 각 태스크 로그를 확인합니다.

## 6) 스케줄링 (평일 21:00 KST)
```bash
chmod +x scripts/schedule_job.sh
./scripts/schedule_job.sh <PROJECT_ID> asia-northeast1
```

## 7) Console(웹)에서 하는 방법 요약
1. **Artifact Registry**: 도커 리포지토리 생성 (asia-northeast1).
2. **Cloud Build**: 소스 업로드 후 *Cloud Build*로 빌드 실행 (cloudbuild.yaml 이용).
3. **Cloud Run → Jobs**: *Create Job* → 이미지 선택 → Tasks=4 → Env( `RANGE_MAX=50000`, `PAUSE_SEC=0.5` ) → Create.
4. Job 상세 화면에서 **Execute** 버튼으로 수동 실행.
5. **Logs** 탭 또는 Logs Explorer에서 결과 확인.
6. **Cloud Scheduler**: HTTP 잡 생성 → URL: `https://run.googleapis.com/apis/run.googleapis.com/v1/namespaces/<PROJECT_ID>/jobs/prime-counter:run` → OIDC 인증 서비스 계정 선택 → 크론 `0 21 * * 1-5`, 타임존 `Asia/Seoul`.

## 8) 확장 아이디어
- GCS에 결과 업로드(google-cloud-storage), BigQuery 적재, 외부 API 호출 등으로 확장.
- 태스크별 파티션 키를 사용한 병렬 크롤링/ETL 실습.
- 실패 재시도, 시간 제한, 메모리/CPU 조정 실험.

---
### 참고
- 본 랩은 기존 파이프라인(여러 파이썬 스크립트를 순차 실행) 구조를 간소화한 교육용 버전입니다.
- 잡과 태스크 환경변수를 적극적으로 활용해 설정을 바꾸며 실험해 보세요.
