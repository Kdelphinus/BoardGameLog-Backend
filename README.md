# Board Game Log

## 개요

- 보드 게임 사진과 내용을 정리할 수 있는 웹 사이트

## 진행 사항

### 2025.02.11

- `User` , `Game` , `GameLog` 모델 구현
- `User` 기본 도메인 구현
  - 생성, 조회, 로그인 기능

### 2025.02.18

- `Game` 기본 도메인 구현
  - 생성, 조회 기능
- 가능 인원을 가능 최대 인원과 가능 최소 인원으로 분리

### ~ 2025.03.10

- `GameLog` 기본 도메인 구현 중
  - 조회 기능
  - 생성 기능은 현재 오류
- `GameLog` DB 모델 수정
  - `text_data` 속성 -> `subject` , `content` 속성으로 분리
  - `during_time` , `participant_num` 속성 -> NULL 허용 불가