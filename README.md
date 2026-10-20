# FilmCraft + Remotion Hybrid Studio

Kiến trúc dựng phim kết hợp (Dual-Engine Hybrid Pipeline) giữa **FilmCraft** (Rust Native NLE - Premiere Pro Alternative) và **Remotion** (React Code-First Motion Graphics - After Effects Alternative).

---

## 🌟 Bản chất kiến trúc Dual-Engine

Hệ thống phân tách nhiệm vụ tối ưu theo thế mạnh của từng công cụ:

1. **FilmCraft (Rust Core / Track V1):**
   - Đảm nhiệm xử lý các luồng video thô 4K/8K, A-roll, B-roll.
   - Quản lý timeline đa track bằng hệ thống thời gian chuẩn **Integer Ticks** (254,016,000,000 ticks/giây).
   - Đồng bộ âm thanh, cân bằng tiếng (audio leveling), lọc tạp âm và color grading.
   - Điều khiển tự động hóa qua giao thức **Model Context Protocol (MCP)**.

2. **Remotion (React Studio / Track V2+):**
   - Đảm nhiệm toàn bộ phần đồ họa động (Motion Graphics, Lower-Thirds, Kinetic Typography, Animated Captions, Biểu đồ/Infographics).
   - Render ra video có kênh trong suốt (**Apple ProRes 4444 Alpha** hoặc **WebM Alpha**).
   - Tự động thay đổi nội dung động (dynamic props) theo từng kịch bản hoặc dữ liệu từ API.

3. **Bridge & Compositor Layer (`bridge/`):**
   - `timeline_bridge.py`: Chuyển đổi chính xác 100% giữa FilmCraft Ticks và Remotion Frames (drift-free).
   - `hybrid_compositor.py`: Tự động gọi Remotion render các lớp overlay trong suốt và ghép nối trực tiếp vào timeline chính tại đúng mốc thời gian.

---

## 🚀 Hướng dẫn sử dụng nhanh

### 1. Cấu trúc thư mục
```
filmcraft-remotion-hybrid/
├── bridge/
│   ├── timeline_bridge.py       # Cầu nối tính toán thời gian Ticks <-> Frames
│   └── hybrid_compositor.py     # Trình kết hợp tự động đa lớp (Multi-track compositor)
├── templates/                   # Mẫu kịch bản kết hợp
├── out/                         # Video thành phẩm xuất ra
│   └── hybrid_master_preview.mp4
├── README.md
└── LICENSE
```

### 2. Chạy quy trình ghép tự động
Từ thư mục dự án:
```powershell
cd "C:\Users\DELL\.gemini\antigravity\scratch\filmcraft-remotion-hybrid"

# Chạy thử nghiệm quy trình composite video thô + Remotion Alpha LowerThird:
python -c "import sys; sys.path.append('bridge'); from hybrid_compositor import composite_video; composite_video('../remotion-studio/public/sample.mp4', '../remotion-studio/out/lowerthird_alpha.mov', 'out/hybrid_master_preview.mp4', 0.5)"
```

---

## 🔗 Liên kết hệ thống
- **Bản Remotion Studio:** `../remotion-studio`
- **Bản Thuần FilmCraft:** `../filmcraft-standalone`
