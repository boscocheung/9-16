#!/bin/bash

# Tập lệnh tự động hóa chuyển đổi video từ 16:9 sang 9:16
# Video Conversion Automation Script

set -e

# Màu sắc cho output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Hàm in tiêu đề
print_title() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Hàm in thành công
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Hàm in lỗi
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Hàm in cảnh báo
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Hàm in thông tin
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Kiểm tra Python
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 không được tìm thấy!"
        exit 1
    fi
    PYTHON_VERSION=$(python3 --version)
    print_success "Tìm thấy $PYTHON_VERSION"
}

# Cài đặt dependencies
install_dependencies() {
    print_title "Cài đặt Dependencies"
    
    if [ ! -d "venv" ]; then
        print_info "Tạo virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    print_info "Cài đặt Python packages..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Kiểm tra FFmpeg
    if command -v ffmpeg &> /dev/null; then
        FFMPEG_VERSION=$(ffmpeg -version | head -n 1)
        print_success "$FFMPEG_VERSION"
    else
        print_warning "FFmpeg không được tìm thấy. Sẽ sử dụng OpenCV thay thế."
        print_info "Để cài đặt FFmpeg:"
        print_info "  Ubuntu/Debian: sudo apt-get install ffmpeg"
        print_info "  macOS: brew install ffmpeg"
        print_info "  Windows: choco install ffmpeg"
    fi
    
    print_success "Cài đặt hoàn tất!"
}

# Chuyển đổi một file
convert_single() {
    local input_file=$1
    local config_file=${2:-"config.yaml"}
    local no_blur=${3:-false}
    
    if [ ! -f "$input_file" ]; then
        print_error "File không tìm thấy: $input_file"
        return 1
    fi
    
    print_info "Chuyển đổi: $input_file"
    
    source venv/bin/activate 2>/dev/null || true
    
    local cmd="python3 video_converter.py \"$input_file\" -c \"$config_file\""
    
    if [ "$no_blur" = true ]; then
        cmd="$cmd --no-blur"
    fi
    
    if eval $cmd; then
        print_success "Chuyển đổi thành công!"
        return 0
    else
        print_error "Chuyển đổi thất bại!"
        return 1
    fi
}

# Chuyển đổi tất cả các file video trong thư mục
convert_batch() {
    local input_dir=${1:-.}
    local config_file=${2:-"config.yaml"}
    local no_blur=${3:-false}
    
    print_title "Chuyển đổi tất cả video trong: $input_dir"
    
    local video_extensions=("mp4" "avi" "mov" "mkv" "flv" "wmv" "webm")
    local converted_count=0
    local failed_count=0
    
    for ext in "${video_extensions[@]}"; do
        while IFS= read -r -d '' file; do
            print_info "Xử lý: $file"
            if convert_single "$file" "$config_file" "$no_blur"; then
                ((converted_count++))
            else
                ((failed_count++))
            fi
        done < <(find "$input_dir" -maxdepth 1 -type f -name "*.$ext" -print0)
    done
    
    print_title "Kết quả"
    print_success "Đã chuyển đổi: $converted_count file"
    if [ $failed_count -gt 0 ]; then
        print_error "Thất bại: $failed_count file"
    fi
}

# Hiển thị thông tin video
show_info() {
    local input_file=$1
    
    if [ ! -f "$input_file" ]; then
        print_error "File không tìm thấy: $input_file"
        return 1
    fi
    
    source venv/bin/activate 2>/dev/null || true
    
    python3 << EOF
import video_converter
import sys

try:
    converter = video_converter.VideoConverter()
    info = converter.get_video_info("$input_file")
    
    print("\n📊 Thông tin video:")
    print(f"  Kích thước: {info['width']}x{info['height']}")
    print(f"  FPS: {info['fps']:.2f}")
    print(f"  Thời lượng: {info['duration']:.2f} giây")
    print(f"  Tỷ lệ: {info['aspect_ratio']:.4f}")
    print()
except Exception as e:
    print(f"❌ Lỗi: {e}", file=sys.stderr)
    sys.exit(1)
EOF
}

# Hiển thị help
show_help() {
    cat << EOF
Tập lệnh chuyển đổi video từ 16:9 sang 9:16

Cách sử dụng: ./convert.sh [LỆNH] [TỲY CHỌN]

LỆnh:
  install         Cài đặt dependencies
  convert FILE    Chuyển đổi một file video
  batch [DIR]     Chuyển đổi tất cả video trong thư mục (mặc định: thư mục hiện tại)
  info FILE       Hiển thị thông tin video
  help            Hiển thị trợ giúp này

Tùy chọn:
  --config FILE   File cấu hình (mặc định: config.yaml)
  --no-blur       Không thêm blur nền

Ví dụ:
  ./convert.sh install
  ./convert.sh convert video.mp4
  ./convert.sh convert video.mp4 --config custom.yaml
  ./convert.sh convert video.mp4 --no-blur
  ./convert.sh batch ./videos
  ./convert.sh info video.mp4

EOF
}

# Main
main() {
    if [ $# -eq 0 ]; then
        print_error "Không có lệnh được cung cấp"
        echo ""
        show_help
        exit 1
    fi
    
    local command=$1
    shift
    
    case "$command" in
        install)
            check_python
            install_dependencies
            ;;
        convert)
            if [ $# -eq 0 ]; then
                print_error "Vui lòng cung cấp đường dẫn file"
                exit 1
            fi
            local input_file=$1
            local config_file="config.yaml"
            local no_blur=false
            
            while [ $# -gt 1 ]; do
                shift
                case "$1" in
                    --config)
                        shift
                        config_file=$1
                        ;;
                    --no-blur)
                        no_blur=true
                        ;;
                esac
            done
            
            check_python
            convert_single "$input_file" "$config_file" "$no_blur"
            ;;
        batch)
            local input_dir="."
            local config_file="config.yaml"
            local no_blur=false
            
            if [ $# -gt 0 ] && [[ ! $1 == --* ]]; then
                input_dir=$1
                shift
            fi
            
            while [ $# -gt 0 ]; do
                case "$1" in
                    --config)
                        shift
                        config_file=$1
                        ;;
                    --no-blur)
                        no_blur=true
                        ;;
                esac
                shift
            done
            
            check_python
            convert_batch "$input_dir" "$config_file" "$no_blur"
            ;;
        info)
            if [ $# -eq 0 ]; then
                print_error "Vui lòng cung cấp đường dẫn file"
                exit 1
            fi
            check_python
            show_info "$1"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Lệnh không xác định: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
