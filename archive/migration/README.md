# garden9 MongoDB → Supabase 마이그레이션 (아카이브)

garden9 의 `slack_messages` 컬렉션을 MongoDB 에서 Supabase PostgreSQL 로 옮긴 기록이다.
**이전은 2026-08-29 에 끝났고 운영은 Supabase 를 쓴다.** 이 디렉터리는 되돌아볼 근거로 남긴다.

> 📌 **`20260830_mongodb_dump/` 는 Vultr 서버를 해지하기 전에 뜬 최종 스냅샷이다.**
> 원본 MongoDB 는 Vultr VPS 안에서만 돌고 있었고 서버가 사라지면 함께 사라진다.
> 그래서 저장소에 함께 보관한다. **다시 만들 수 없는 데이터다.**

## 덤프

| | |
| --- | --- |
| 채취일 | 2026-08-30 |
| 출처 | Vultr VPS (`158.247.226.178`) 의 `docker-garden-db-1` 컨테이너 |
| DB.컬렉션 | `garden9.slack_messages` |
| 문서 수 | **1078건** |
| 크기 | 1,890,178 bytes |
| 방식 | `mongodump --db garden9 --collection slack_messages` |

문서 수는 2026-08-29 이전 검증 때의 건수와 같다. **이전 이후 원본에 쓰기가 없었다는 뜻**이다.

## ★ `20260830_local_only_23/` — 운영에 없던 23건

**운영 MongoDB 에는 없고 개발용 로컬 DB 에만 있던 기록이다.** 별도로 보관한다.

`~/projects/docker-garden8/db` (2024-07 시점의 로컬 mongo 볼륨, 199MB)를 정리하려다
버려도 되는지 확인하는 과정에서 나왔다. **버릴 수 없었다.**

| | |
| --- | --- |
| 건수 | **23건** |
| 날짜 | 2023-08-31, 09-01, 09-30, 10-01 |
| 작성자 | prravda 7, gitsunmin 4, iwanhae 3, kangju2000 3, junho85 2, skj2366 2, anonymousRecords 1, nullist0 1 |
| 운영 덤프와 겹침 | **0건** |

### 버려도 되는지 세 번 확인했고, 세 번 다 아니었다

1. **행사 기간 밖인가** → 아니다. garden9 는 `2023-08-13 ~ 11-21` (100일)인데 **23건 전부 기간 안**이다.
2. **그 날짜가 통째로 빠졌나** → 아니다. 운영에도 그 날들 기록이 있다.

   | 날짜 | 운영 | 로컬 | 로컬 전용 |
   | --- | --- | --- | --- |
   | 2023-08-31 | 6 | 12 | 6 |
   | 2023-09-01 | 4 | 5 | 1 |
   | 2023-09-30 | 12 | 18 | 6 |
   | 2023-10-01 | 13 | 23 | 10 |

3. **같은 커밋이 다른 `ts` 로 중복 저장된 건가** → 아니다. 운영 덤프의 커밋 해시 **1,540개**와
   대조했는데 **23건 전부 운영에 없는 커밋**이다.

작성자 8명은 전원 `users.yaml` 17명 명단에 있다. 테스트 데이터가 아니라 실제 참가자의 실제 커밋이다.

### 왜 빠졌나 — 정황이지 단정은 아니다

로컬은 **2023-11-06 에서 수집이 멈춘 더 오래된 스냅샷**(672건)인데도, 저 4일만 운영(1,078건)보다 많다.
그리고 **월말과 월초에만 몰려 있다.** Slack 히스토리를 기간 단위로 가져올 때 경계 처리가 어긋나면
딱 이런 모양이 된다. 다만 **수집 코드를 직접 확인한 것은 아니다.**

### 아직 복원하지 않았다

**현재 서비스 중인 garden9 출석부에는 이 23건이 반영돼 있지 않다.** 운영 MongoDB 를 그대로
Supabase 로 옮겼기 때문이다. 3년 전 기록이라 순위가 바뀌지는 않지만 데이터는 어긋난 상태다.

복원하려면 이 BSON 을 Supabase `garden9` 스키마에 넣으면 된다. **운영 데이터를 건드리는 일이라
보존과 분리해 두었다.**

### 복원

```bash
mongorestore --db garden9 --collection slack_messages 20260830_mongodb_dump/slack_messages.bson
```

BSON 을 직접 읽으려면 `migrate_to_supabase.py` 가 쓰는 `bson` 패키지를 그대로 쓰면 된다.

## 파일 구조

```
archive/migration/
├── README.md                     # 이 파일
├── requirements.txt              # Python 의존성
├── migration_config.yaml.sample  # 설정 템플릿
├── migration_config.yaml         # 실제 설정 — ★ gitignore, 커밋 금지
├── supabase_schema.sql           # 스키마 DDL
├── migrate_to_supabase.py        # 이전 스크립트
├── 20260830_mongodb_dump/        # ★ Vultr 종료 전 최종 스냅샷 (1,078건)
│   ├── slack_messages.bson
│   └── slack_messages.metadata.json
└── 20260830_local_only_23/       # ★ 운영에 없던 23건 (아래 참조)
    ├── slack_messages.bson
    └── slack_messages.metadata.json
```

## 스키마 설계에서 신경 쓴 것

**`raw` JSONB 컬럼에 원문을 통째로 보존한다.** garden9 는 garden6 에 없던 필드가 있어
(`app_id`, `author_name` 최상위, 스레드 관련 일부) 컬럼만으로는 유실된다.
자주 쓰는 것은 컬럼으로 빼고 **원문 전체는 `raw` 에 남겨** 나중에 꺼낼 수 있게 했다.

## ⚠️ 이전에서 겪은 함정

**타임존.** `MongoTools` 는 `CodecOptions(tz_aware=True, tzinfo=Asia/Seoul)` 로 읽고 있었는데
PostgreSQL 경로에는 그 변환이 없어 **API 응답 시각이 9시간 어긋났다**
(`13:43:47.371` vs `22:43:47.371+09:00`).

★ **출석부 화면은 멀쩡해 보였다.** `/attendance/api/gets` 응답을 운영과 대조해서야 드러났다.
`db_tools.py` 에 UTC → KST 변환을 넣어 맞췄고, 근거로 남기려고 `mongo_tools.py` 는 지우지 않았다.

## 검증

운영(MongoDB) 대 테스트(Supabase) 를 바이트 단위로 대조했다.

- 문서 수 1078건 일치
- `ts` 집합 차집합 0
- 작성자별 건수 불일치 0
- `raw` 원문 누락 필드 0
- 출석부 메인, `api/users`, `api/gets` 일치
- **개인별 커밋 페이지 전원 일치**

## 관련

- 같은 방식의 선행 사례 — [junho85/garden6 archive/migration](https://github.com/junho85/garden6/tree/master/archive/migration)
- Vultr → NAS 이전은 2026-08-30 완료. garden4~10 전부 Synology NAS 에서 돌고 Supabase 를 본다.
