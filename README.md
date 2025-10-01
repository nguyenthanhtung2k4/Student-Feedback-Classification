<h1 align="center">Phân loại cảm xúc sinh viên</h1>

<div align="center">

<p align="center">
  <img src="reluts/logoDaiNam.png" alt="DaiNam University Logo" width="200"/>
  <img src="reluts/LogoAIoTLab.png" alt="AIoTLab Logo" width="170"/>
</p>

[![Made by AIoTLab](https://img.shields.io/badge/Made%20by%20AIoTLab-blue?style=for-the-badge)](https://www.facebook.com/DNUAIoTLab)
[![Fit DNU](https://img.shields.io/badge/Fit%20DNU-green?style=for-the-badge)](https://fitdnu.net/)
[![DaiNam University](https://img.shields.io/badge/DaiNam%20University-red?style=for-the-badge)](https://dainam.edu.vn)

</div>

<h2 align="center">Phân loại cảm xúc sinh viên bằng phương pháp học máy</h2>

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
## Models
-  File Huấn luyện nằm trong  notebook [Tại đây](./Train/train.ipynb)


## Run Web
```bash
cd Web

python app.py
```

## Truy cập
```bash
http://127.0.0.1:5000
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
└─ Train                   # Follder chứa file tiền xử lý +  huấn luyện
│  └─ train.ipynb          # NoteBook Dùng huấn luyện
"# Student-Feedback-Classification" 
```


## Thank you !
