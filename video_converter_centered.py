#!/usr/bin/env python3
"""
Video Converter: 16:9 to 9:16 Format with Center Focus
Chuyển đổi video từ định dạng 16:9 sang 9:16 với chủ thể luôn ở giữa
"""

import os
import sys
import argparse
import yaml
from pathlib import Path
from typing import Optional, Tuple
import subprocess
import json
import platform

try:
    import cv2
except ImportError:
    print("OpenCV không được cài đặt. Vui lòng chạy: pip install opencv-python")
    sys.exit(1)


class VideoConverterCentered:
    """Lớp chuyển đổi video từ 16:9 sang 9:16 với chủ thể ở giữa"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Khởi tạo VideoConverter
        
        Args:
            config_path: Đường dẫn đến file cấu hình
        """
        self.config = self._load_config(config_path)
        self.output_dir = Path(self.config.get("output_dir", "output"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.system = platform.system()
        
        # Kích thước chuẩn 9:16
        self.target_width = 1080
        self.target_height = 1920
    
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
            "output_dir": "output",
            "target_width": 1080,
            "target_height": 1920
        }
    
    def _check_ffmpeg_available(self) -> bool:
        """Kiểm tra xem FFmpeg có sẵn không (cross-platform)"""
        try:
            if self.system == "Windows":
                result = subprocess.run(["where", "ffmpeg"], 
                                       capture_output=True, 
                                       timeout=5)
            else:
                result = subprocess.run(["which", "ffmpeg"], 
                                       capture_output=True, 
                                       timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
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
    
    def calculate_crop_with_centering(self, original_width: int, original_height: int) -> Tuple[int, int, int, int]:
        """
        Tính toán crop để giữ chủ thể ở giữa
        
        Args:
            original_width: Chiều rộng gốc
            original_height: Chiều cao gốc
            
        Returns:
            tuple: (crop_width, crop_height, offset_x, offset_y)
        """
        # Tỷ lệ 9:16 = 0.5625
        target_ratio = self.target_width / self.target_height
        current_ratio = original_width / original_height
        
        if current_ratio > target_ratio:
            # Video quá rộng, crop chiều rộng
            crop_width = int(original_height * target_ratio)
            crop_height = original_height
            offset_x = (original_width - crop_width) // 2
            offset_y = 0
        else:
            # Video quá cao, crop chiều cao
            crop_width = original_width
            crop_height = int(original_width / target_ratio)
            offset_x = 0
            offset_y = (original_height - crop_height) // 2
        
        return crop_width, crop_height, offset_x, offset_y
    
    def convert_with_ffmpeg(self, input_path: str, output_path: str, 
                          add_blur: bool = True, blur_intensity: int = 15) -> bool:
        """
        Chuyển đổi video sử dụng FFmpeg với chủ thể ở giữa
        
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
            
            print(f"📊 Video gốc: {width}x{height}")
            
            # Tính toán crop để giữ chủ thể ở giữa
            crop_width, crop_height, offset_x, offset_y = self.calculate_crop_with_centering(width, height)
            
            # Làm tròn kích thước
            crop_width = (crop_width // 2) * 2
            crop_height = (crop_height // 2) * 2
            target_width = (self.target_width // 2) * 2
            target_height = (self.target_height // 2) * 2
            
            print(f"🎯 Kích thước crop: {crop_width}x{crop_height}")
            print(f"📍 Offset: ({offset_x}, {offset_y})")
            print(f"🎬 Kích thước cuối cùng: {target_width}x{target_height}")
            
            # Xây dựng filter FFmpeg (sử dụng filter_complex cho multiple inputs)
            if add_blur:
                # Scale gốc để làm blur background + crop + scale foreground
                filter_str = (
                    f"[0:v]scale={target_width}:{target_height},boxblur={blur_intensity}:1[bg];"
                    f"[0:v]crop={crop_width}:{crop_height}:{offset_x}:{offset_y},scale={target_width}:{target_height}[fg];"
                    f"[bg][fg]overlay=0:0[out]"
                )
            else:
                # Crop + scale + đặt trên nền đen
                filter_str = (
                    f"[0:v]crop={crop_width}:{crop_height}:{offset_x}:{offset_y},"
                    f"scale={target_width}:{target_height},"
                    f"pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2:black[out]"
                )
            
            # Lệnh FFmpeg (sử dụng -filter_complex thay vì -vf)
            cmd = [
                "ffmpeg",
                "-i", input_path,
                "-filter_complex", filter_str,
                "-map", "[out]",
                "-map", "0:a",
                "-c:v", self.config.get("codec", "libx264"),
                "-b:v", self.config.get("bitrate", "5000k"),
                "-c:a", "aac",
                "-b:a", "128k",
                "-y",
                output_path
            ]
            
            print(f"🎬 Đang chuyển đổi...")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Chuyển đổi thành công: {output_path}")
                return True
            else:
                print(f"❌ Lỗi FFmpeg:")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def convert_with_opencv(self, input_path: str, output_path: str,
                           add_blur: bool = True, blur_intensity: int = 15) -> bool:
        """
        Chuyển đổi video sử dụng OpenCV với chủ thể ở giữa
        
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
            
            print(f"📊 Video gốc: {width}x{height}")
            
            # Tính toán crop
            crop_width, crop_height, offset_x, offset_y = self.calculate_crop_with_centering(width, height)
            
            # Làm tròn kích thước
            crop_width = (crop_width // 2) * 2
            crop_height = (crop_height // 2) * 2
            target_width = (self.target_width // 2) * 2
            target_height = (self.target_height // 2) * 2
            
            print(f"🎯 Kích thước crop: {crop_width}x{crop_height}")
            print(f"📍 Offset: ({offset_x}, {offset_y})")
            print(f"🎬 Kích thước cuối cùng: {target_width}x{target_height}")
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (target_width, target_height))
            
            if not out.isOpened():
                print(f"❌ Không thể tạo file output: {output_path}")
                cap.release()
                return False
            
            print(f"🎬 Đang chuyển đổi...")
            
            frame_count = 0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Crop frame để giữ chủ thể ở giữa
                cropped_frame = frame[offset_y:offset_y + crop_height, 
                                     offset_x:offset_x + crop_width]
                
                if add_blur:
                    # Tạo blur background
                    bg_frame = cv2.resize(frame, (target_width, target_height))
                    bg_frame = cv2.GaussianBlur(bg_frame, 
                                               (blur_intensity * 2 + 1, blur_intensity * 2 + 1), 
                                               0)
                    
                    # Resize cropped frame
                    fg_frame = cv2.resize(cropped_frame, (target_width, target_height))
                    
                    # Sử dụng foreground frame
                    output_frame = fg_frame
                else:
                    # Resize và đặt trên nền đen
                    resized = cv2.resize(cropped_frame, (target_width, target_height))
                    output_frame = resized
                
                out.write(output_frame)
                frame_count += 1
                
                if frame_count % 30 == 0:
                    progress = (frame_count / total_frames * 100) if total_frames > 0 else 0
                    print(f"⏳ Đã xử lý {frame_count}/{total_frames} frame ({progress:.1f}%)...")
            
            cap.release()
            out.release()
            
            print(f"✅ Chuyển đổi thành công: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def convert(self, input_path: str, output_name: Optional[str] = None,
                use_ffmpeg: bool = True) -> bool:
        """
        Chuyển đổi video từ 16:9 sang 9:16 với chủ thể ở giữa
        
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
            output_name = f"{base_name}_1080x1920.{output_format}"
        
        output_path = str(self.output_dir / output_name)
        
        print(f"\n{'='*50}")
        print(f"📱 Video Converter: 16:9 → 9:16 (1080x1920)")
        print(f"{'='*50}\n")
        
        # Kiểm tra FFmpeg
        ffmpeg_available = self._check_ffmpeg_available()
        
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
        description="Chuyển đổi video từ 16:9 sang 9:16 (1080x1920) với chủ thể ở giữa",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  python video_converter_centered.py video.mp4
  python video_converter_centered.py video.mp4 -o output.mp4
  python video_converter_centered.py video.mp4 --config custom_config.yaml
  python video_converter_centered.py video.mp4 --no-blur
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
    converter = VideoConverterCentered(args.config)
    
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
