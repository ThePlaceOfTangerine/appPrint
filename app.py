import streamlit as st
import pandas as pd

# MOCK DATA
def load_mock_data():
    data = [
        {"time": 1, "ip": "192.168.1.5", "tokens": "partnerId=xwhZ,version=6.1", "label": "TuneIn Radio"},
        {"time": 2, "ip": "192.168.1.5", "tokens": "u_audio=high", "label": None},
        {"time": 3, "ip": "192.168.1.5", "tokens": "ad_request=true", "label": None},

        {"time": 10, "ip": "192.168.1.10", "tokens": "game_id=angry_birds,u_audio=0", "label": "Angry Birds"},
        {"time": 11, "ip": "192.168.1.10", "tokens": "rovio_verify=true", "label": None},
        {"time": 12, "ip": "192.168.1.10", "tokens": "ad_request=true", "label": None},

        {"time": 20, "ip": "192.168.1.20", "tokens": "whatsapp_msg=true,contact_sync=enabled", "label": "WhatsApp"},
        {"time": 21, "ip": "192.168.1.20", "tokens": "media_upload=image", "label": None},
    ]
    return pd.DataFrame(data)

# NORMALIZE CSV
def normalize_dataframe(df):
    if 'app_label' in df.columns:
        df = df.rename(columns={'app_label': 'label', 'flow_id': 'time'})
    if 'ip' not in df.columns:
        df['ip'] = '192.168.1.' + (df['time'] % 250 + 1).astype(str)
    return df

def parse_tokens(tokens_str):
    tokens_str = str(tokens_str)
    tokens = [t.strip() for t in tokens_str.replace(',', ' ').split()]
    # Trích xuất key từ cặp key=value [cite: 82, 101]
    return [t.split('=')[0] for t in tokens if t]

# MAP (FLOW GROUPING)
def train_map(df, TG=10):
    map_repo = {}
    # Gom nhóm luồng xung quanh luồng 'neo' (anchor) [cite: 116, 127]
    anchors = df[df['label'].notna()]
    
    for _, anchor in anchors.iterrows():
        app = anchor['label']
        anchor_time = anchor['time']
        anchor_ip = anchor['ip']

        # Tiêu chí: cùng IP nguồn và trong khoảng TG giây [cite: 129]
        group = df[
            (df['ip'] == anchor_ip) &
            (abs(df['time'] - anchor_time) <= TG)
        ]

        for _, g_row in group.iterrows():
            tokens = parse_tokens(g_row['tokens'])
            for token in tokens:
                if token not in map_repo:
                    map_repo[token] = {"total": 0}
                
                # Lan truyền danh tính (Identity Propagation) 
                map_repo[token][app] = map_repo[token].get(app, 0) + 1
                map_repo[token]["total"] += 1

    return map_repo

# SCORE
def compute_score_standard(map_repo, tokens):
    scores = {}
    apps = set()
    for t in map_repo:
        apps.update([k for k in map_repo[t] if k != "total"])

    for app in apps:
        total_score = 0
        for t in tokens:
            if t in map_repo:
                # Công thức (1): (MAP_tx / MAP_t_all) / số_app_liên_kết [cite: 178, 180]
                ratio = map_repo[t].get(app, 0) / map_repo[t]["total"]
                num_apps = len([k for k in map_repo[t] if k != "total"])
                total_score += ratio / num_apps
        
        scores[app] = total_score
    return scores

# ECCENTRICITY
def compute_eccentricity(scores):
    if not scores or len(scores) < 2:
        return 1.0, next(iter(scores)) if scores else "Không xác định"

    sorted_apps = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    (x1, s1), (x2, s2) = sorted_apps[0], sorted_apps[1]

    if s1 == 0: return 0, x1
    
    # phi = (score_1st - score_2nd) / score_1st [cite: 187]
    phi = (s1 - s2) / s1
    return phi, x1

# UI
st.set_page_config(page_title="AppPrint Lab", layout="wide")
st.title("AppPrint")

if 'repo' not in st.session_state: st.session_state.repo = None

tab1, tab2 = st.tabs(["🚀 Phase 1: MAP Learning", "🔍 Phase 2: SCORE Identification"])

with tab1:
    st.header("Thuật toán MAP (Học dấu vân tay)")
    uploaded_file = st.file_uploader("Upload dữ liệu mạng (CSV)", type="csv")
    df = normalize_dataframe(pd.read_csv(uploaded_file)) if uploaded_file else load_mock_data()
    
    st.write("### Dữ liệu lưu lượng mạng:")
    st.dataframe(df, use_container_width=True)

    tg_val = st.slider("Ngưỡng thời gian gom nhóm $T_G$ (giây)", 1, 30, 10)
    
    if st.button("Bắt đầu huấn luyện MAP"):
        st.session_state.repo = train_map(df, tg_val)
        st.session_state.df = df
        st.success("Huấn luyện hoàn tất theo quy trình Paper! [cite: 113]")
        
        st.write("### Kho lưu trữ MAP (Tokens learned):")
        # Chuyển đổi hiển thị hàng ngang cho MAP
        map_display = []
        for t, data in st.session_state.repo.items():
            row = {"Token": t, "Total": data['total']}
            row.update({k: v for k, v in data.items() if k != 'total'})
            map_data = map_display.append(row)
        st.dataframe(pd.DataFrame(map_display).fillna(0), use_container_width=True)

with tab2:
    st.header("Thuật toán SCORE (Identification)")
    if st.session_state.repo is None:
        st.warning("⚠️ Vui lòng thực hiện Phase 1 trước!")
    else:
        st.write("Nhập IP và thời gian để tạo **Flow Set** cần nhận diện[cite: 154, 159].")
        col_in1, col_in2 = st.columns(2)
        target_ip = col_in1.text_input("Địa chỉ IP nguồn", "192.168.1.5")
        target_time = col_in2.number_input("Mốc thời gian (Time slot)", value=2)

        if st.button("🔍 Thực hiện SCORE"):
            test_df = st.session_state.df
            # Gom nhóm Flow Set trong cửa sổ TS = 10s [cite: 173]
            relevant_flows = test_df[(test_df['ip'] == target_ip) & (abs(test_df['time'] - target_time) <= 10)]
            
            tokens_in_set = []
            for _, r in relevant_flows.iterrows(): tokens_in_set.extend(parse_tokens(r['tokens']))
            
            if not tokens_in_set:
                st.error(f"❌ Không tìm thấy tokens cho IP {target_ip} tại thời điểm {target_time}. Hãy thử mốc thời gian khác (ví dụ: 11, 21, 46).")
            else:
                st.info(f"**Tokens tìm thấy trong Flow Set:** `{tokens_in_set}`")
                
                # Tính toán điểm số và độ lệch
                all_scores = compute_score_standard(st.session_state.repo, tokens_in_set)
                phi, best_app = compute_eccentricity(all_scores)

                # Hiển thị các chỉ số chính
                m1, m2, m3 = st.columns(3)
                m1.metric("Ứng dụng dự đoán", best_app)
                m2.metric("Độ lệch (Eccentricity)", f"{phi:.2f}")
                m3.info("Ngưỡng tin cậy: $\Phi > 0.3$ [cite: 196]")

                # HIỂN THỊ CẢ KẾT QUẢ ĐỘ CHÍNH XÁC THẤP
                st.write("### 📊 Bảng điểm chi tiết (SCORE Table - Hàng ngang):")
                score_horizontal = pd.DataFrame([all_scores]).round(4)
                st.dataframe(score_horizontal, use_container_width=True)
                
                # Cảnh báo dựa trên ngưỡng thực nghiệm của paper
                if phi > 0.3:
                    st.success(f"🎯 Ứng dụng được xác định rõ ràng: **{best_app}**")
                else:
                    st.warning(f"⚠️ Độ lệch thấp ({phi:.2f} < 0.3). Kết quả không chắc chắn nhưng ứng dụng tiềm năng nhất là: **{best_app}**")
                
                # Biểu đồ so sánh
                st.bar_chart(pd.Series(all_scores))