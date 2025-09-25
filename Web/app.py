from flask import Flask, request, jsonify, render_template
import joblib
from sentence_transformers import SentenceTransformer
import numpy as np
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# ------------- Load model -------------
save_sentiments = joblib.load("multioutput_brf_model.pkl") # danh gia sentiments
save_topic = joblib.load("multioutput_xgboost_model.pkl") # Danh gia   topic 
model = save_sentiments.get("model")
sentiment_encoder = save_sentiments.get("sentiment_encoder")   # may be None
topic_encoder = save_topic.get("topic_encoder")           # may be None
sbert_model_name = save_sentiments.get("sbert_model_name", "paraphrase-multilingual-mpnet-base-v2")
sbert = SentenceTransformer(sbert_model_name)

# ------------- Mappings (fallback) -------------
topic_map = {
    0: "Giảng viên",
    1: "Chương trình đào tạo",
    2: "Cơ sở vật chất",
    3: "Khác"
}
sentiment_map = {
    0: "Tiêu cực",
    1: "Trung lập",
    2: "Tích cực"
}

# ------------- DB init -------------
DB_PATH = "history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # BƯỚC 1: Đảm bảo bảng 'history' được tạo trước
    cur.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        sentiment TEXT,
        topic TEXT,
        created_at TEXT
    )
    """)
    conn.commit()

    # BƯỚC 2: Thêm cột 'ip_address' nếu chưa tồn tại
    try:
        cur.execute("ALTER TABLE history ADD COLUMN ip_address TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        # Bỏ qua lỗi nếu cột đã tồn tại (lỗi này chỉ xảy ra sau khi chạy thành công lần đầu)
        pass
    
    conn.close()

init_db()

# ------------- Helpers -------------
def safe_extract_ids(y_pred):
    """
    Trả về (sentiment_id, topic_id) là python int hoặc (int, None)
    Hỗ trợ nhiều dạng output của model.predict(...)
    """
    arr = np.asarray(y_pred)
    if arr.ndim == 2 and arr.shape[1] >= 2:
        sid = int(arr[0, 0])
        tid = int(arr[0, 1])
        return sid, tid
    if arr.ndim == 1 and arr.size >= 2:
        sid = int(arr[0])
        tid = int(arr[1])
        return sid, tid
    if arr.ndim == 2 and arr.shape[1] == 1:
        sid = int(arr[0, 0])
        return sid, None
    if arr.ndim == 1 and arr.size == 1:
        sid = int(arr[0])
        return sid, None
    raise ValueError(f"Unexpected prediction shape: {arr.shape}")

def id_to_label_sentiment(sid):
    # try encoder first
    try:
        if sentiment_encoder is not None:
            lab = sentiment_encoder.inverse_transform([sid])[0]
            # Normalize possible English labels to Vietnamese
            lab_lower = str(lab).lower()
            if "pos" in lab_lower or "positive" in lab_lower or lab_lower == "2":
                return sentiment_map[2]
            if "neu" in lab_lower or "neutral" in lab_lower or lab_lower == "1":
                return sentiment_map[1]
            if "neg" in lab_lower or "negative" in lab_lower or lab_lower == "0":
                return sentiment_map[0]
            return str(lab)
    except Exception:
        pass
    # fallback numeric mapping
    return sentiment_map.get(int(sid), str(sid))

def id_to_label_topic(tid):
    try:
        if topic_encoder is not None:
            lab = topic_encoder.inverse_transform([tid])[0]
            # If lab is descriptive in English, map to Vietnamese if possible
            lab_lower = str(lab).lower()
            if "lecturer" in lab_lower or "giang" in lab_lower:
                return topic_map[0]
            if "training" in lab_lower or "program" in lab_lower or "đào tạo" in lab_lower:
                return topic_map[1]
            if "facility" in lab_lower or "cơ sở" in lab_lower:
                return topic_map[2]
            # fallback: return encoder label
            return str(lab)
    except Exception:
        pass
    # fallback mapping by id
    return topic_map.get(int(tid), str(tid))

# ------------- Routes -------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        payload = request.get_json(force=True)
        text = (payload.get("text") or "").strip()
        if not text:
            return jsonify({"error": "Vui lòng nhập văn bản"}), 400

        # Lấy địa chỉ IP của client
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)

        # encode
        emb = sbert.encode([text], convert_to_numpy=True)
        emb = np.array(emb)

        # predict
        y_pred = model.predict(emb)  # may be ndarray/list
        sid, tid = safe_extract_ids(y_pred)

        # convert to labels (Vietnamese)
        sentiment_label = id_to_label_sentiment(sid)
        topic_label = id_to_label_topic(tid) if tid is not None else None

        # save to DB
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO history (text, sentiment, topic, created_at, ip_address) VALUES (?, ?, ?, ?, ?)",
            (text, str(sentiment_label), str(topic_label), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ip_address)
        )
        conn.commit()
        conn.close()

        return jsonify({
            "sentiment": str(sentiment_label),
            "topic": str(topic_label)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/history", methods=["GET"])
def history():
    """
    Trả JSON các bản ghi (dùng cho trang chính).
    """
    try:
        limit = int(request.args.get("limit", 50))
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, text, sentiment, topic, created_at, ip_address FROM history ORDER BY id DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
        out = []
        for r in rows:
            out.append({
                "id": int(r[0]),
                "text": r[1],
                "sentiment": r[2],
                "topic": r[3],
                "created_at": r[4],
                "ip_address": r[5]
            })
        return jsonify(out)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------- Admin pages & APIs -------------
@app.route("/admin")
def admin_page():
    return render_template("admin.html")

@app.route("/admin/api/history", methods=["GET"])
def admin_history_api():
    """
    Params optional: date_from, date_to (YYYY-MM-DD), sentiment, topic, limit
    """
    try:
        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")
        sentiment = request.args.get("sentiment")
        topic = request.args.get("topic")
        limit = int(request.args.get("limit", 200))

        sql = "SELECT id, text, sentiment, topic, created_at, ip_address FROM history WHERE 1=1 "
        params = []
        if date_from:
            sql += " AND substr(created_at,1,10) >= ? "
            params.append(date_from)
        if date_to:
            sql += " AND substr(created_at,1,10) <= ? "
            params.append(date_to)
        if sentiment:
            sql += " AND sentiment = ? "
            params.append(sentiment)
        if topic:
            sql += " AND topic = ? "
            params.append(topic)
        sql += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()
        conn.close()

        out = []
        for r in rows:
            out.append({"id": int(r[0]), "text": r[1], "sentiment": r[2], "topic": r[3], "created_at": r[4], "ip_address": r[5]})
        return jsonify(out)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/api/delete", methods=["POST"])
def admin_delete():
    try:
        data = request.get_json(force=True)
        rid = int(data.get("id"))
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("DELETE FROM history WHERE id = ?", (rid,))
        conn.commit()
        conn.close()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/api/stats", methods=["GET"])
def admin_stats():
    """
    Trả thống kê tổng: counts per sentiment, per topic
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        # sentiment counts
        cur.execute("SELECT sentiment, COUNT(*) FROM history GROUP BY sentiment")
        sent_rows = cur.fetchall()
        sent_counts = {r[0]: int(r[1]) for r in sent_rows}

        # topic counts
        cur.execute("SELECT topic, COUNT(*) FROM history GROUP BY topic")
        top_rows = cur.fetchall()
        top_counts = {r[0]: int(r[1]) for r in top_rows}

        conn.close()
        return jsonify({"sentiment_counts": sent_counts, "topic_counts": top_counts})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/api/trend", methods=["GET"])
def admin_trend():
    """
    Trả dữ liệu trend theo ngày cho last N days (default 30)
    Format: { dates: [...], datasets: { "Tiêu cực":[...], "Trung lập":[...], "Tích cực":[...] } }
    """
    try:
        days = int(request.args.get("days", 30))
        start_dt = (datetime.now() - timedelta(days=days-1)).strftime("%Y-%m-%d")  # inclusive
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT substr(created_at,1,10) as d, sentiment, COUNT(*) 
            FROM history
            WHERE substr(created_at,1,10) >= ?
            GROUP BY d, sentiment
            ORDER BY d ASC
        """, (start_dt,))
        rows = cur.fetchall()
        conn.close()

        # build date list
        dates = []
        base = datetime.now() - timedelta(days=days-1)
        for i in range(days):
            dates.append((base + timedelta(days=i)).strftime("%Y-%m-%d"))

        datasets = { sentiment_map[0]: [0]*days, sentiment_map[1]: [0]*days, sentiment_map[2]: [0]*days }
        date_index = {d:i for i,d in enumerate(dates)}
        for d, sent, cnt in rows:
            idx = date_index.get(d)
            if idx is not None:
                # sent stored as Vietnamese possibly; try map
                s = str(sent)
                if s in datasets:
                    datasets[s][idx] = int(cnt)
                else:
                    # try to map english label to vietnamese
                    sl = s.lower()
                    if "pos" in sl or "tich" in sl:
                        datasets[sentiment_map[2]][idx] = int(cnt)
                    elif "neu" in sl or "trung" in sl:
                        datasets[sentiment_map[1]][idx] = int(cnt)
                    elif "neg" in sl or "tiêu" in sl:
                        datasets[sentiment_map[0]][idx] = int(cnt)
        return jsonify({"dates": dates, "datasets": datasets})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------- Run -------------
if __name__ == "__main__":
    app.run(debug=True)