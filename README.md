# AppPrint
## 📂 Cấu trúc thư mục

```bash
AppPrint-Demo/
│
├── app.py                      # File chính chạy Streamlit dashboard
├── appprint_mock_dataset.csv   # Dataset mô phỏng AppPrint
├── mock_data.csv               # Dữ liệu mẫu bổ sung
├── requirements.txt            # Danh sách thư viện Python
├── Dockerfile                  # Cấu hình Docker image
├── docker-compose.yml          # Cấu hình Docker Compose
├── .gitignore                  # Bỏ qua file không cần push lên GitHub
└── README.md                   # Tài liệu hướng dẫn dự án
```

---

## 🚀 Hướng dẫn cài đặt và chạy ứng dụng

Có thể chạy dự án bằng hai cách:

1. Chạy bằng Docker.
2. Chạy trực tiếp bằng môi trường Python local.

Khuyến khích sử dụng Docker để tránh lỗi môi trường.

---

## Cách 1: Chạy bằng Docker

### Yêu cầu

Máy cần cài đặt sẵn:

* Docker
* Docker Compose

### Bước 1: Clone project

```bash
git clone <repository-url>
cd <project-folder>
```

Ví dụ:

```bash
git clone https://github.com/<your-username>/AppPrint-Demo.git
cd AppPrint-Demo
```

### Bước 2: Build và chạy ứng dụng

```bash
docker compose up -d --build
```

### Bước 3: Truy cập ứng dụng

Sau khi container chạy thành công, mở trình duyệt và truy cập:

```bash
http://localhost:8501
```

### Bước 4: Xem trạng thái container

```bash
docker compose ps
```

### Bước 5: Dừng ứng dụng

```bash
docker compose down
```

---

## Cách 2: Chạy trực tiếp bằng Python local

### Yêu cầu

Máy cần cài đặt:

* Python 3.9 trở lên
* pip

### Bước 1: Clone project

```bash
git clone <repository-url>
cd <project-folder>
```

### Bước 2: Tạo môi trường ảo

Trên Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Trên Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Bước 3: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### Bước 4: Chạy ứng dụng

```bash
streamlit run app.py
```

### Bước 5: Truy cập dashboard

```bash
http://localhost:8501
```
