# Crypto Graves Backend API

Crypto Graves 프로젝트의 FastAPI 기반 백엔드 서버입니다.

## 기능

- Web3 지갑 인증 (서명 기반, JWT 없이)
- 손실 데이터 등록 및 검증
- NFT/밈 자산 발행
- 랭킹 시스템
- 거래 시스템

## 설치 및 실행

### 1. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정

```bash
cp env.example .env
# .env 파일을 편집하여 실제 값들을 설정
```

### 4. Docker 컨테이너 실행

```bash
# PostgreSQL 컨테이너 시작
docker-compose up -d

# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f
```

### 5. 서버 실행

```bash
# 개발 모드
uvicorn app.main:app --reload

# 프로덕션 모드
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Docker 서비스

### PostgreSQL
- **포트**: ${POSTGRES_PORT}
- **데이터베이스**: ${POSTGRES_DB}
- **사용자**: ${POSTGRES_USER}

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:${SERVER_PORT}/docs
- ReDoc: http://localhost:${SERVER_PORT}/redoc

## 주요 엔드포인트

### 인증 (POC용 - JWT 없이)
- `POST /api/v1/auth/wallet-auth` - 지갑 서명 인증
- `GET /api/v1/auth/me?wallet_address={address}` - 지갑 주소로 사용자 정보 조회

### 손실 데이터
- `POST /api/v1/losses` - 손실 데이터 등록
- `GET /api/v1/losses` - 손실 데이터 목록 조회
- `GET /api/v1/losses/{loss_id}` - 특정 손실 데이터 조회
- `PUT /api/v1/losses/{loss_id}` - 손실 데이터 업데이트
- `POST /api/v1/losses/{loss_id}/verify` - 손실 데이터 검증
- `POST /api/v1/losses/upload-transaction` - 트랜잭션 데이터 업로드

## 데이터베이스 스키마

### users 테이블
- id (int, primary key)
- uuid (uuid, unique)
- wallet_address (varchar(42), unique)
- username (varchar(100), nullable)
- email (varchar(255), nullable)
- role (enum: user, admin, moderator)
- total_loss (decimal(20,8))
- total_gain (decimal(20,8))
- profile_image_url (text, nullable)
- bio (text, nullable)
- is_active (boolean)
- created_at (timestamp)
- updated_at (timestamp)

### losses 테이블
- id (int, primary key)
- uuid (uuid, unique)
- user_id (int, foreign key)
- user_uuid (uuid, foreign key)
- asset_name (varchar(100))
- asset_ticker (varchar(20))
- loss_amount (decimal(20,8))
- loss_amount_mon (decimal(20,8))
- transaction_hash (varchar(66))
- transaction_data (jsonb)
- signature (text)
- status (enum: pending, verified, rejected)
- verified_at (timestamp, nullable)
- verified_by (int, foreign key, nullable)
- verified_by_uuid (uuid, foreign key, nullable)
- nft_token_id (int, nullable)
- nft_contract_address (varchar(42), nullable)
- notes (text, nullable)
- created_at (timestamp)
- updated_at (timestamp)

### rankings 테이블
- id (int, primary key)
- uuid (uuid, unique)
- user_id (int, foreign key)
- user_uuid (uuid, foreign key)
- period_type (enum: daily, weekly, monthly)
- period_start (timestamp)
- period_end (timestamp)
- total_loss (decimal(20,8))
- rank_position (int)
- reward_amount (decimal(20,8), nullable)
- reward_paid (boolean)
- created_at (timestamp)
- updated_at (timestamp)

### trades 테이블
- id (int, primary key)
- uuid (uuid, unique)
- seller_id (int, foreign key)
- seller_uuid (uuid, foreign key)
- buyer_id (int, foreign key, nullable)
- buyer_uuid (uuid, foreign key, nullable)
- nft_id (int, foreign key)
- nft_uuid (uuid, foreign key)
- price (decimal)
- status (enum: listed, sold, cancelled)
- transaction_hash (text, nullable)
- created_at (timestamp)
- updated_at (timestamp)

## 환경변수

필요한 환경변수들을 `.env` 파일에 설정하세요:

```env
# Database Configuration (PostgreSQL)
POSTGRES_DB=crypto_graves
POSTGRES_USER=crypto_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_PORT=5432
DATABASE_URL=postgresql://crypto_user:your_secure_password@localhost:5432/crypto_graves

# Web3 Configuration
MONAD_RPC_URL=https://rpc.testnet.monad.xyz
MONAD_CHAIN_ID=1337
PRIVATE_KEY=your_private_key_for_contract_deployment

# JWT Configuration (POC에서는 사용하지 않음)
# SECRET_KEY=your_super_secret_key_for_jwt_tokens_make_it_long_and_random
# ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Crypto Graves API

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# File Storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# Telegram Bot (Optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# Application Configuration
DEBUG=true
LOG_LEVEL=info
```

## 개발 도구

### 데이터베이스 관리
```bash
# PostgreSQL에 직접 연결
docker exec -it crypto_graves_postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}
```

### 컨테이너 관리
```bash
# 컨테이너 중지
docker-compose down

# 컨테이너와 볼륨 삭제
docker-compose down -v

# 특정 서비스만 재시작
docker-compose restart postgres
```

## 문제 해결

### 데이터베이스 연결 오류
```bash
# 컨테이너 상태 확인
docker-compose ps

# PostgreSQL 로그 확인
docker-compose logs postgres

# 데이터베이스 재초기화
docker-compose down -v
docker-compose up -d
```

### 포트 충돌
```env
# .env 파일에서 포트 변경
POSTGRES_PORT=5433
SERVER_PORT=8001
```

## POC 인증 방식

현재 POC에서는 JWT 토큰 대신 지갑 주소 기반의 간단한 인증을 사용합니다:

1. **지갑 연결**: 사용자가 지갑을 연결하고 서명
2. **서명 검증**: 서버에서 서명을 검증하여 지갑 주소 확인
3. **사용자 생성/조회**: 지갑 주소로 사용자 정보 생성 또는 조회
4. **API 호출**: 지갑 주소를 파라미터로 전달하여 API 호출

이 방식은 개발 속도를 높이고 복잡성을 줄이기 위한 임시 방안입니다.
