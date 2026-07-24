#!/usr/bin/env python3
"""
Video Converter: 16:9 to 9:16 Format
Chuyển đổi video từ định dạng 16:9 sang 9:16
"""

import os
import sys
import argparse
import yaml
from pathlib import Path
from typing import Optional, Tuple
import subprocess
import json

try:
    import cv2
except ImportError:
    print("OpenCV không được cài đặt. Vui lòng chạy: pip install opencv-python")
    sys.exit(1)


class VideoConverter:
    """Lớp chuyển đổi video từ 16:9 sang 9:16"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Khởi tạo VideoConverter
        
        Args:
            config_path: Đường dẫn đến file cấu hình
        """
        self.config = self._load_config(config_path)
        self.output_dir = Path(self.config.get("output_dir", "output"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self, config_path: str) -> dict:
        """Tải file cấu hình YAML"""
        if not os.path.exists(config_path):
            print(f"⚠️  File cấu hình không tìm thấy: {config_path}")
            return self._get_default_config()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"❌ Lỗi khi tải cấu hình: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """Trả về cấu hình mặc định"""
        return {
            "output_format": "mp4",
            "codec": "libx264",
            "quality": "high",
            "bitrate": "5000k",
            "fps": 30,
            "add_blur": True,
            "blur_intensity": 15,
            "output_dir": "output"
        }
    
    def get_video_info(self, video_path: str) -> dict:
        """
        Lấy thông tin video
        
        Args:
            video_path: Đường dẫn đến file video
            
        Returns:
            dict: Thông tin video (width, height, fps, duration)
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video không tìm thấy: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Không thể mở video: {video_path}")
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        return {
            "width": width,
            "height": height,
            "fps": fps,
            "duration": duration,
            "frame_count": frame_count,
            "aspect_ratio": width / height if height > 0 else 0
        }
    
    def calculate_dimensions(self, original_width: int, original_height: int) -> Tuple[int, int, Tuple[int, int, int, int]]:
        """
        Tính toán kích thước mới cho định dạng 9:16
        
        Args:
            original_width: Chiều rộng gốc
            original_height: Chiều cao gốc
            
        Returns:
            tuple: (new_width, new_height, (top, bottom, left, right))
        """
        # Định dạng 9:16 có tỷ lệ 0.5625
        target_ratio = 9 / 16
        current_ratio = original_width / original_height
        
        if current_ratio > target_ratio:
            # Video quá rộng, cần crop chiều rộng
            new_width = int(original_height * target_ratio)
            new_height = original_height
            left = (original_width - new_width) // 2
            right = original_width - new_width - left
            top = 0
            bottom = 0
        else:
            # Video quá cao, thêm blur ở trên dưới
            new_width = original_width
            new_height = int(original_width / target_ratio)
            top = (new_height - original_height) // 2
            bottom = new_height - original_height - top
            left = 0
            right = 0
        
        return new_width, new_height, (top, bottom, left, right)
    
    def convert_with_ffmpeg(self, input_path: str, output_path: str, 
                          add_blur: bool = True, blur_intensity: int = 15) -> bool:
        """
        Chuyển đổi video sử dụng FFmpeg
        
        Args:
            input_path: Đường dẫn video đầu vào
            output_path: Đường dẫn video đầu ra
            add_blur: Thêm blur nền (True/False)
            blur_intensity: Cường độ blur (1-25)
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            # Lấy thông tin video
            video_info = self.get_video_info(input_path)
            width = video_info["width"]
            height = video_info["height"]
            
            # Tính toán kích thước mới
            new_width, new_height, (top, bottom, left, right) = self.calculate_dimensions(width, height)
            
            # Làm tròn kích thước để chia hết cho 2 (yêu cầu của FFmpeg)
            new_width = (new_width // 2) * 2
            new_height = (new_height // 2) * 2
            
            # Xây dựng filter FFmpeg
            if top > 0 or bottom > 0:
                # Thêm blur nền trên dưới
                if add_blur:
                    # Tạo nền blur
                    filter_str = (
                        f"[0:v]scale={new_width}:{new_height},"
                        f"boxblur={blur_intensity}:1[bg];"
                        f"[0:v]scale={width}:{height}[fg];"
                        f"[bg][fg]overlay=(W-w)/2:(H-h)/2"
                    )
                else:
                    # Nền đen
                    filter_str = (
                        f"pad={new_width}:{new_height}:(ow-iw)/2:(oh-ih)/2:black"
                    )
            else:
                # Chỉ crop chiều rộng
                crop_width = new_width
                crop_height = height
                filter_str = (
                    f"crop={crop_width}:{crop_height}:(iw-ow)/2:0"
                )
            
            # Lệnh FFmpeg
            cmd = [
                "ffmpeg",
                "-i", input_path,
                "-vf", filter_str,
                "-c:v", self.config.get("codec", "libx264"),
                "-b:v", self.config.get("bitrate", "5000k"),
                "-c:a", "aac",
                "-b:a", "128k",
                "-y",
                output_path
            ]
            
            print(f"🎬 Đang chuyển đổi: {input_path}")
            print(f"📊 Kích thước mới: {new_width}x{new_height}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Chuyển đổi thành công: {output_path}")
                return True
            else:
                print(f"❌ Lỗi FFmpeg: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return False
    
    def convert_with_opencv(self, input_path: str, output_path: str,
                           add_blur: bool = True, blur_intensity: int = 15) -> bool:
        """
        Chuyển đổi video sử dụng OpenCV (fallback nếu FFmpeg không có)
        
        Args:
            input_path: Đường dẫn video đầu vào
            output_path: Đường dẫn video đầu ra
            add_blur: Thêm blur nền (True/False)
            blur_intensity: Cường độ blur (1-25)
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            cap = cv2.VideoCapture(input_path)
            
            if not cap.isOpened():
                print(f"❌ Không thể mở video: {input_path}")
                return False
            
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            new_width, new_height, (top, bottom, left, right) = self.calculate_dimensions(width, height)
            
            # Làm tròn kích thước
            new_width = (new_width // 2) * 2
            new_height = (new_height // 2) * 2
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (new_width, new_height))
            
            if not out.isOpened():
                print(f"❌ Không thể tạo file output: {output_path}")
                cap.release()
                return False
            
            print(f"🎬 Đang chuyển đổi: {input_path}")
            print(f"📊 Kích thước mới: {new_width}x{new_height}")
            
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Resize frame
                if top > 0 or bottom > 0:
                    # Thêm padding trên dưới
                    if add_blur:
                        # Blur nền
                        frame_resized = cv2.resize(frame, (new_width, new_height - top - bottom))
                        blur_frame = cv2.resize(frame, (new_width, new_height))
                        blur_frame = cv2.GaussianBlur(blur_frame, (blur_intensity * 2 + 1, blur_intensity * 2 + 1), 0)
                        blur_frame[top:top + new_height - top - bottom] = frame_resized
                        frame = blur_frame
                    else:
                        # Nền đen
                        frame_resized = cv2.resize(frame, (new_width, new_height - top - bottom))
                        frame = cv2.copyMakeBorder(frame_resized, top, bottom, 0, 0, 
                                                   cv2.BORDER_CONSTANT, value=(0, 0, 0))
                else:
                    # Crop chiều rộng
                    frame = frame[:, left:left + new_width]
                
                out.write(frame)
                frame_count += 1
                
                if frame_count % 30 == 0:
                    print(f"⏳ Đã xử lý {frame_count} frame...")
            
            cap.release()
            out.release()
            
            print(f"✅ Chuyển đổi thành công: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return False
    
    def convert(self, input_path: str, output_name: Optional[str] = None,
                use_ffmpeg: bool = True) -> bool:
        """
        Chuyển đổi video từ 16:9 sang 9:16
        
        Args:
            input_path: Đường dẫn video đầu vào
            output_name: Tên file đầu ra (tùy chọn)
            use_ffmpeg: Sử dụng FFmpeg nếu có sẵn (True/False)
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        if not os.path.exists(input_path):
            print(f"❌ File không tìm thấy: {input_path}")
            return False
        
        # Tạo tên file output
        if output_name is None:
            base_name = Path(input_path).stem
            output_format = self.config.get("output_format", "mp4")
            output_name = f"{base_name}_9-16.{output_format}"
        
        output_path = str(self.output_dir / output_name)
        
        # Kiểm tra FFmpeg
        ffmpeg_available = subprocess.run(["which", "ffmpeg"], 
                                         capture_output=True).returncode == 0
        
        if use_ffmpeg and ffmpeg_available:
            add_blur = self.config.get("add_blur", True)
            blur_intensity = self.config.get("blur_intensity", 15)
            return self.convert_with_ffmpeg(input_path, output_path, add_blur, blur_intensity)
        else:
            if use_ffmpeg and not ffmpeg_available:
                print("⚠️  FFmpeg không tìm thấy, sử dụng OpenCV...")
            add_blur = self.config.get("add_blur", True)
            blur_intensity = self.config.get("blur_intensity", 15)
            return self.convert_with_opencv(input_path, output_path, add_blur, blur_intensity)


def main():
    """Hàm main"""
    parser = argparse.ArgumentParser(
        description="Chuyển đổi video từ 16:9 sang 9:16",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  python video_converter.py video.mp4
  python video_converter.py video.mp4 -o output.mp4
  python video_converter.py video.mp4 --config custom_config.yaml
  python video_converter.py video.mp4 --no-blur
        """
    )
    
    parser.add_argument("input", help="Đường dẫn video đầu vào")
    parser.add_argument("-o", "--output", help="Tên file đầu ra (tùy chọn)")
    parser.add_argument("-c", "--config", default="config.yaml", 
                       help="Đường dẫn file cấu hình (mặc định: config.yaml)")
    parser.add_argument("--no-blur", action="store_true", 
                       help="Không thêm blur nền, sử dụng nền đen")
    parser.add_argument("--no-ffmpeg", action="store_true",
                       help="Không sử dụng FFmpeg, dùng OpenCV")
    
    args = parser.parse_args()
    
    # Khởi tạo converter
    converter = VideoConverter(args.config)
    
    # Nếu --no-blur, tắt blur trong cấu hình
    if args.no_blur:
        converter.config["add_blur"] = False
    
    # Chuyển đổi
    success = converter.convert(
        args.input,
        output_name=args.output,
        use_ffmpeg=not args.no_ffmpeg
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
