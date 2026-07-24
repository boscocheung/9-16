#!/usr/bin/env python3
"""
Batch Video Converter: Tự động hóa chuyển đổi hàng loạt
Xử lý tất cả video trong thư mục và các thư mục con
"""

import os
import sys
import argparse
from pathlib import Path
from video_converter import VideoConverter
import logging

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('conversion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BatchConverter:
    """Lớp chuyển đổi hàng loạt"""
    
    # Các định dạng video được hỗ trợ
    SUPPORTED_FORMATS = {
        '.mp4', '.avi', '.mov', '.mkv', '.flv', 
        '.wmv', '.webm', '.m4v', '.3gp', '.ogv'
    }
    
    def __init__(self, config_path: str = "config.yaml"):
        """Khởi tạo BatchConverter"""
        self.converter = VideoConverter(config_path)
        self.converted_count = 0
        self.failed_count = 0
        self.skipped_count = 0
    
    def is_video_file(self, file_path: Path) -> bool:
        """Kiểm tra xem file có phải là video không"""
        return file_path.suffix.lower() in self.SUPPORTED_FORMATS
    
    def process_file(self, input_path: Path, output_dir: Path = None) -> bool:
        """
        Xử lý một file video
        
        Args:
            input_path: Đường dẫn file input
            output_dir: Thư mục output (tùy chọn)
            
        Returns:
            bool: True nếu thành công
        """
        try:
            # Kiểm tra file đầu ra
            base_name = input_path.stem
            output_name = f"{base_name}_9-16{input_path.suffix}"
            output_path = (output_dir or self.converter.output_dir) / output_name
            
            if output_path.exists():
                logger.warning(f"⏭️  Bỏ qua (file đã tồn tại): {input_path}")
                self.skipped_count += 1
                return True
            
            logger.info(f"🎬 Chuyển đổi: {input_path}")
            
            # Chuyển đổi
            success = self.converter.convert(
                str(input_path),
                output_name=output_name
            )
            
            if success:
                self.converted_count += 1
                logger.info(f"✅ Thành công: {output_path}")
                return True
            else:
                self.failed_count += 1
                logger.error(f"❌ Thất bại: {input_path}")
                return False
                
        except Exception as e:
            self.failed_count += 1
            logger.error(f"❌ Lỗi: {e}")
            return False
    
    def process_directory(self, input_dir: str, recursive: bool = True, 
                         output_dir: str = None) -> None:
        """
        Xử lý tất cả video trong thư mục
        
        Args:
            input_dir: Thư mục input
            recursive: Tìm kiếm trong thư mục con (True/False)
            output_dir: Thư mục output (tùy chọn)
        """
        input_path = Path(input_dir)
        
        if not input_path.exists():
            logger.error(f"❌ Thư mục không tìm thấy: {input_dir}")
            return
        
        if not input_path.is_dir():
            logger.error(f"❌ Không phải thư mục: {input_dir}")
            return
        
        output_path = Path(output_dir) if output_dir else None
        if output_path:
            output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📁 Quét thư mục: {input_path}")
        logger.info(f"🔄 Tìm kiếm recursive: {recursive}")
        
        # Tìm tất cả file video
        if recursive:
            video_files = [f for f in input_path.rglob('*') 
                          if f.is_file() and self.is_video_file(f)]
        else:
            video_files = [f for f in input_path.glob('*') 
                          if f.is_file() and self.is_video_file(f)]
        
        if not video_files:
            logger.warning("⚠️  Không tìm thấy file video nào")
            return
        
        logger.info(f"📊 Tìm thấy {len(video_files)} file video")
        
        # Xử lý từng file
        for i, video_file in enumerate(video_files, 1):
            logger.info(f"\n📍 [{i}/{len(video_files)}]")
            self.process_file(video_file, output_path)
        
        # In kết quả
        self.print_summary()
    
    def process_list(self, file_list: str, output_dir: str = None) -> None:
        """
        Xử lý danh sách file từ text file
        
        Args:
            file_list: Đường dẫn đến file chứa danh sách
            output_dir: Thư mục output (tùy chọn)
        """
        try:
            with open(file_list, 'r', encoding='utf-8') as f:
                files = [line.strip() for line in f if line.strip()]
            
            if not files:
                logger.warning("⚠️  File danh sách rỗng")
                return
            
            logger.info(f"📊 Tìm thấy {len(files)} file trong danh sách")
            
            output_path = Path(output_dir) if output_dir else None
            if output_path:
                output_path.mkdir(parents=True, exist_ok=True)
            
            for i, file_path in enumerate(files, 1):
                logger.info(f"\n📍 [{i}/{len(files)}]")
                path = Path(file_path)
                
                if not path.exists():
                    logger.warning(f"⏭️  Bỏ qua (không tìm thấy): {file_path}")
                    self.skipped_count += 1
                    continue
                
                if not self.is_video_file(path):
                    logger.warning(f"⏭️  Bỏ qua (không phải video): {file_path}")
                    self.skipped_count += 1
                    continue
                
                self.process_file(path, output_path)
            
            self.print_summary()
            
        except Exception as e:
            logger.error(f"❌ Lỗi: {e}")
    
    def print_summary(self) -> None:
        """In tóm tắt kết quả"""
        logger.info("\n" + "="*50)
        logger.info("📊 TÓM TẮT KẾT QUẢ")
        logger.info("="*50)
        logger.info(f"✅ Thành công: {self.converted_count}")
        logger.info(f"❌ Thất bại: {self.failed_count}")
        logger.info(f"⏭️  Bỏ qua: {self.skipped_count}")
        logger.info(f"📁 Output: {self.converter.output_dir}")
        logger.info("="*50)


def main():
    """Hàm main"""
    parser = argparse.ArgumentParser(
        description="Chuyển đổi hàng loạt video từ 16:9 sang 9:16",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  python batch_convert.py -d ./videos
  python batch_convert.py -d ./videos -o ./output
  python batch_convert.py -d ./videos --no-recursive
  python batch_convert.py -f file_list.txt
  python batch_convert.py -f file_list.txt -o ./output
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--directory", help="Thư mục chứa video")
    group.add_argument("-f", "--file-list", help="File chứa danh sách video")
    
    parser.add_argument("-o", "--output", help="Thư mục output")
    parser.add_argument("-c", "--config", default="config.yaml",
                       help="File cấu hình (mặc định: config.yaml)")
    parser.add_argument("--no-recursive", action="store_true",
                       help="Không tìm kiếm trong thư mục con")
    
    args = parser.parse_args()
    
    # Khởi tạo batch converter
    batch = BatchConverter(args.config)
    
    # Xử lý
    if args.directory:
        batch.process_directory(
            args.directory,
            recursive=not args.no_recursive,
            output_dir=args.output
        )
    elif args.file_list:
        batch.process_list(args.file_list, output_dir=args.output)


if __name__ == "__main__":
    main()
