# BTL phân loại  cảm xúc sinh viên

## Setup
- Yêu cầu python >= 3.11
- Tạo môi trường ảo:
```bash
python -m venv envStudents
```
- Vào môi trường: 
```bash
cd .\envStudents\Scripts\activate
```
-  Cài môi trường: 
```pip 
pip install -r requirements.txt
```

## Run File
```bash
python app.py
```


## Cấu trúc Foloder
```bash
sentiment-web/
├─ app.py                           # Flask app (backend)
├─ multioutput_xgboost_model.pkl    # mô hình nhận dạng topic
├─ multioutput_brf_model.pkl        # mô hình nhận dạng sentiments
├─ multioutput_brf_V2_model.pkl     # mô hình bổ sung (chưa áp dụng)
├─ requirements.txt                 # Setup    
├─ templates/
│  └─ admin.js                # JavaScript thao thác Fe vs Be
│  └─ script.js               # JavaScript thao thác Fe vs Be
│  └─ style.css               # Css giao diện  Index.html
├─ templates/
│  └─ index.html           # frontend giao diện chính
│  └─ admin.html           # frontend Admin
└─ feedbacks.db            # (tự tạo khi chạy lần đầu) Database chứa các nội dung text
"# Student-Feedback-Classification" 
```


## Thank you !