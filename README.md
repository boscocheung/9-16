# 📱 Video Converter: 16:9 → 9:16

Công cụ chuyên nghiệp để chuyển đổi video từ định dạng 16:9 (ngang) sang 9:16 (dọc). Hoàn hảo cho TikTok, Instagram Reels, YouTube Shorts, và các ứng dụng mobile khác.

## ✨ Tính năng

- ✅ **Chuyển đổi 16:9 → 9:16**: Tự động điều chỉnh tỷ lệ khung hình
- 🎨 **Blur Background**: Thêm nền blur thông minh thay vì đen
- 🔄 **Xử lý Hàng Loạt**: Chuyển đổi nhiều file cùng lúc
- ⚙️ **Cấu hình Linh Hoạt**: YAML config cho các tùy chọn tùy chỉnh
- 🚀 **FFmpeg & OpenCV**: Hỗ trợ cả hai engine
- 📊 **Thông tin Video**: Xem chi tiết video trước khi chuyển đổi
- 📝 **Logging**: Ghi nhật ký đầy đủ
- 🎯 **CLI Thân Thiện**: Interface dễ sử dụng

## 📋 Yêu cầu

- Python 3.7+
- FFmpeg (tùy chọn, nhưng khuyến nghị để chất lượng tốt hơn)
- OpenCV (bắt buộc)

## 🚀 Cài Đặt

### 1. Clone Repository

```bash
git clone https://github.com/boscocheung/9-16.git
cd 9-16
```

### 2. Cài Đặt Dependencies

**Sử dụng Script (Dễ nhất):**

```bash
chmod +x convert.sh
./convert.sh install
```

**Hoặc Thủ Công:**

```bash
# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# hoặc
venv\Scripts\activate     # Windows

# Cài đặt packages
pip install -r requirements.txt
```

### 3. Cài Đặt FFmpeg (Khuyến nghị)

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
```bash
choco install ffmpeg
```

Hoặc tải từ: https://ffmpeg.org/download.html

## 📖 Cách Sử Dụng

### Option 1: Sử Dụng Script Shell (Đơn Giản)

```bash
# Chuyển đổi một file
./convert.sh convert video.mp4

# Chuyển đổi với cấu hình tùy chỉnh
./convert.sh convert video.mp4 --config custom.yaml

# Chuyển đổi không blur (nền đen)
./convert.sh convert video.mp4 --no-blur

# Chuyển đổi tất cả video trong thư mục
./convert.sh batch ./videos

# Xem thông tin video
./convert.sh info video.mp4
```

### Option 2: Python Trực Tiếp

```bash
# Chuyển đổi một file
python3 video_converter.py video.mp4

# Với tên output tùy chỉnh
python3 video_converter.py video.mp4 -o output.mp4

# Với cấu hình tùy chỉnh
python3 video_converter.py video.mp4 -c config.yaml

# Không thêm blur (nền đen)
python3 video_converter.py video.mp4 --no-blur

# Sử dụng OpenCV thay vì FFmpeg
python3 video_converter.py video.mp4 --no-ffmpeg
```

### Option 3: Chuyển Đổi Hàng Loạt

```bash
# Chuyển đổi tất cả video trong thư mục
python3 batch_convert.py -d ./videos

# Chuyển đổi không recursive
python3 batch_convert.py -d ./videos --no-recursive

# Chuyển đổi với output directory tùy chỉnh
python3 batch_convert.py -d ./videos -o ./output

# Chuyển đổi từ danh sách file
python3 batch_convert.py -f file_list.txt

# Xem log
tail -f conversion.log
```

## ⚙️ Cấu Hình

Chỉnh sửa `config.yaml`:

```yaml
# Định dạng đầu ra
output_format: "mp4"

# Codec video (libx264, libx265, libvpx, libvpx-vp9)
codec: "libx264"

# Chất lượng (low, medium, high, very_high)
quality: "high"

# Bit rate
bitrate: "5000k"

# FPS
fps: 30

# Thêm blur nền
add_blur: true

# Cường độ blur (1-25)
blur_intensity: 15

# Thư mục output
output_dir: "output"
```

### Tùy Chọn Codec

- **libx264**: H.264 (tương thích tốt, phổ biến)
- **libx265**: H.265/HEVC (nén tốt hơn, file nhỏ hơn)
- **libvpx**: VP8 (WebM)
- **libvpx-vp9**: VP9 (WebM, chất lượng tốt)

### Cường Độ Blur

- **5-10**: Blur nhẹ
- **15-20**: Blur trung bình (mặc định)
- **25+**: Blur mạnh

## 📚 Ví Dụ

### Ví Dụ 1: Chuyển đổi đơn giản

```bash
./convert.sh convert my_video.mp4
```

**Kết quả**: `output/my_video_9-16.mp4` (với blur nền)

### Ví Dụ 2: Chuyển đổi cho TikTok

```bash
./convert.sh convert video.mp4 --no-blur
```

**Kết quả**: `output/video_9-16.mp4` (nền đen)

### Ví Dụ 3: Xử lý hàng loạt

```bash
# Tạo file danh sách
echo "video1.mp4" > videos.txt
echo "video2.mp4" >> videos.txt
echo "video3.mp4" >> videos.txt

# Chuyển đổi
python3 batch_convert.py -f videos.txt -o ./mobile_videos
```

### Ví Dụ 4: Chuyên nghiệp (H.265, chất lượng cao)

```yaml
# custom.yaml
output_format: "mp4"
codec: "libx265"
bitrate: "8000k"
fps: 60
add_blur: true
blur_intensity: 20
```

```bash
./convert.sh convert video.mp4 --config custom.yaml
```

## 📊 Thông Tin Output

Trước khi chuyển đổi, xem thông tin:

```bash
./convert.sh info video.mp4
```

**Output:**
```
📊 Thông tin video:
  Kích thước: 1920x1080
  FPS: 30.00
  Thời lượng: 60.50 giây
  Tỷ lệ: 1.7778
```

## 🔍 Hỗ Trợ Format

- **Input**: MP4, AVI, MOV, MKV, FLV, WMV, WebM, M4V, 3GP, OGV
- **Output**: MP4, WebM, MKV (tùy theo cấu hình)

## 🐛 Khắc Phục Sự Cố

### Lỗi: "FFmpeg không tìm thấy"

**Giải pháp**: Cài đặt FFmpeg hoặc sử dụng flag `--no-ffmpeg`

```bash
./convert.sh convert video.mp4 --no-ffmpeg
```

### Lỗi: "OpenCV không được cài đặt"

**Giải pháp**:
```bash
pip install opencv-python
```

### Video output không có âm thanh

**Giải pháp**: Đây là vấn đề FFmpeg, hãy chạy lại hoặc kiểm tra codec âm thanh

### Quá chậm

**Giải pháp**: Giảm bitrate hoặc fps trong `config.yaml`

```yaml
bitrate: "2500k"  # Giảm từ 5000k
fps: 24           # Giảm từ 30
```

## 📈 Hiệu Năng

| Tác Vụ | Thời Gian | Ghi Chú |
|--------|-----------|---------|
| Chuyển 1 video (2 phút) | ~1-2 phút | Phụ thuộc vào codec |
| Xử lý 10 video | ~15-20 phút | Tuần tự |
| Xử lý 10 video (FFmpeg) | ~8-10 phút | Tối ưu hơn |

**Mẹo**: Sử dụng FFmpeg để tốc độ nhanh hơn

## 💡 Tips & Tricks

### Tạo Preset Tùy Chỉnh

```bash
# Tạo config cho social media
cat > social_media.yaml << EOF
output_format: "mp4"
codec: "libx264"
bitrate: "4000k"
fps: 30
add_blur: true
blur_intensity: 15
output_dir: "social_output"
EOF

./convert.sh convert video.mp4 --config social_media.yaml
```

### Chuyển đổi từ URL

```bash
# Download video trước
yt-dlp -f best <URL> -o video.mp4

# Sau đó chuyển đổi
./convert.sh convert video.mp4
```

### Chuyển đổi Hàng Loạt Với Find

```bash
find ./videos -name "*.mp4" | while read file; do
    ./convert.sh convert "$file"
done
```

## 📝 Changelog

### v1.0.0 (2024-01)
- ✅ Chuyển đổi 16:9 → 9:16
- ✅ Support FFmpeg & OpenCV
- ✅ Batch processing
- ✅ YAML configuration
- ✅ Shell script automation

## 📄 License

MIT License - xem tệp LICENSE để chi tiết

## 🤝 Đóng Góp

Hứng thú đóng góp? Tạo pull request hoặc mở issue!

## 📞 Liên Hệ

- 📧 Email: boscocheung@example.com
- 🐛 Issues: https://github.com/boscocheung/9-16/issues

## 🙏 Cảm Ơn

- FFmpeg team
- OpenCV community
- Tất cả những ai đóng góp!

---

**Tạo video đẹp cho mobile! 📱✨**
