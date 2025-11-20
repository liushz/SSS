#!/usr/bin/env python3
import os
import oss2
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger


class OSSFileManager:
    """简化的OSS文件管理器"""
    
    def __init__(
        self,
        oss_access_key_id: str = None,
        oss_access_key_secret: str = None,
        oss_region: str = None,
        oss_bucket_name: str = None
    ):
        """
        初始化OSS文件管理器
        
        Args:
            oss_access_key_id: OSS访问密钥ID
            oss_access_key_secret: OSS访问密钥Secret
            oss_region: OSS区域端点
            oss_bucket_name: OSS存储桶名称
        """
        # 从环境变量获取配置
        self.access_key_id = oss_access_key_id or os.getenv('OSS_ACCESS_KEY_ID')
        self.access_key_secret = oss_access_key_secret or os.getenv('OSS_ACCESS_KEY_SECRET')
        self.region = oss_region or os.getenv('OSS_REGION', 'http://oss-cn-shanghai.aliyuncs.com')
        self.bucket_name = oss_bucket_name or os.getenv('OSS_BUCKET_NAME', 'opencompass')
        
        if not self.access_key_id or not self.access_key_secret:
            raise ValueError("OSS访问密钥未设置。请设置 OSS_ACCESS_KEY_ID 和 OSS_ACCESS_KEY_SECRET 环境变量。")
        
        # 初始化OSS客户端
        auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        self.bucket = oss2.Bucket(auth, self.region, self.bucket_name)
        
        logger.info(f"OSS初始化成功: {self.bucket_name} @ {self.region}")
    
    def list_files(
        self, 
        oss_dir: str = "", 
        after_date: datetime = None,
        file_extension: str = None
    ) -> List[Dict]:
        """
        列出OSS目录中的文件
        
        Args:
            oss_dir: OSS目录路径
            after_date: 只返回此日期之后的文件
            file_extension: 文件扩展名过滤 (如 ".json")
            
        Returns:
            文件信息列表
        """
        try:
            files = []
            
            # 确保目录路径以 / 结尾
            if oss_dir and not oss_dir.endswith('/'):
                oss_dir += '/'
            
            # 列出对象
            for obj in oss2.ObjectIterator(self.bucket, prefix=oss_dir):
                # 跳过目录本身
                if obj.key.endswith('/'):
                    continue
                
                # 文件扩展名过滤
                if file_extension and not obj.key.endswith(file_extension):
                    continue
                
                # 日期过滤
                if after_date and obj.last_modified < after_date:
                    continue
                
                file_info = {
                    'key': obj.key,
                    'name': os.path.basename(obj.key),
                    'size': obj.size,
                    'last_modified': obj.last_modified,
                    'etag': obj.etag
                }
                files.append(file_info)
            
            logger.info(f"找到 {len(files)} 个文件在 {oss_dir}")
            return files
            
        except Exception as e:
            logger.error(f"列出文件失败: {e}")
            raise
    
    def download_file(self, oss_file_path: str, local_file_path: str) -> bool:
        """
        从OSS下载文件到本地
        
        Args:
            oss_file_path: OSS文件路径
            local_file_path: 本地文件路径
            
        Returns:
            下载是否成功
        """
        try:
            # 确保本地目录存在
            local_dir = os.path.dirname(local_file_path)
            if local_dir:
                os.makedirs(local_dir, exist_ok=True)
            
            # 下载文件
            self.bucket.get_object_to_file(oss_file_path, local_file_path)
            
            logger.info(f"下载成功: {oss_file_path} -> {local_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"下载文件失败: {oss_file_path} -> {local_file_path}, 错误: {e}")
            return False
    
    def upload_file_to_object(
        self, 
        local_file_path: str, 
        oss_file_path: str,
        replace: bool = False
    ) -> bool:
        """
        上传本地文件到OSS
        
        Args:
            local_file_path: 本地文件路径
            oss_file_path: OSS文件路径
            replace: 是否替换已存在的文件
            
        Returns:
            上传是否成功
        """
        try:
            # 检查本地文件是否存在
            if not os.path.exists(local_file_path):
                logger.error(f"本地文件不存在: {local_file_path}")
                return False
            
            # 检查OSS文件是否存在
            if not replace and self.bucket.object_exists(oss_file_path):
                logger.warning(f"OSS文件已存在: {oss_file_path}")
                return False
            
            # 上传文件
            self.bucket.put_object_from_file(oss_file_path, local_file_path)
            
            logger.info(f"上传成功: {local_file_path} -> {oss_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"上传文件失败: {local_file_path} -> {oss_file_path}, 错误: {e}")
            return False
    
    def file_exists(self, oss_file_path: str) -> bool:
        """
        检查OSS文件是否存在
        
        Args:
            oss_file_path: OSS文件路径
            
        Returns:
            文件是否存在
        """
        try:
            return self.bucket.object_exists(oss_file_path)
        except Exception as e:
            logger.error(f"检查文件存在性失败: {oss_file_path}, 错误: {e}")
            return False
    
    def download_file_content(self, oss_file_path: str) -> Optional[bytes]:
        """
        下载OSS文件内容到内存
        
        Args:
            oss_file_path: OSS文件路径
            
        Returns:
            文件内容（字节）或None
        """
        try:
            result = self.bucket.get_object(oss_file_path)
            content = result.read()
            logger.info(f"下载文件内容成功: {oss_file_path} ({len(content)} bytes)")
            return content
        except Exception as e:
            logger.error(f"下载文件内容失败: {oss_file_path}, 错误: {e}")
            return None
    
    def upload_file_content(self, content: str, object_key: str) -> bool:
        """
        直接上传字符串内容到OSS
        
        Args:
            content: 要上传的字符串内容
            object_key: OSS对象键（文件路径）
            
        Returns:
            上传是否成功
        """
        try:
            # 将字符串转换为字节
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            else:
                content_bytes = content
            
            # 直接上传内容到OSS
            self.bucket.put_object(object_key, content_bytes)
            
            logger.info(f"上传内容成功: {object_key} ({len(content_bytes)} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"上传内容失败: {object_key}, 错误: {e}")
            return False


    def upload_file(self, local_file_path: str, oss_file_path: str) -> bool:
        """
        上传本地文件到OSS（别名方法）
        
        Args:
            local_file_path: 本地文件路径
            oss_file_path: OSS文件路径
            
        Returns:
            上传是否成功
        """
        return self.upload_file_to_object(local_file_path, oss_file_path, replace=True)
    
    def copy_file(self, source_path: str, target_path: str) -> bool:
        """
        在OSS内部复制文件
        
        Args:
            source_path: 源文件路径
            target_path: 目标文件路径
            
        Returns:
            复制是否成功
        """
        try:
            # 使用copy_object进行OSS内部复制
            self.bucket.copy_object(
                self.bucket_name,  # 源bucket
                source_path,       # 源文件路径
                target_path        # 目标文件路径
            )
            logger.info(f"文件复制成功: {source_path} -> {target_path}")
            return True
        except Exception as e:
            logger.error(f"文件复制失败: {source_path} -> {target_path}, 错误: {e}")
            return False

    def list_latest_files_by_date(
        self,
        object_dir: str = "",
        max_num_files: int = 100,
        suffix: str = ".json",
        date_pattern: str = r".*",
        file_date_format: str = "%Y-%m-%d"
    ) -> List[str]:
        """
        列出OSS目录中按日期排序的文件

        Args:
            object_dir: OSS目录路径
            max_num_files: 最大文件数量
            suffix: 文件后缀
            date_pattern: 日期匹配模式
            file_date_format: 日期格式

        Returns:
            文件路径列表（最新的在前面）
        """
        try:
            # 使用现有的list_files方法
            files = self.list_files(
                oss_dir=object_dir,
                file_extension=suffix
            )

            # 提取文件名
            filenames = []
            for file_info in files:
                filename = file_info['name']
                # 简单的文件名匹配（不使用复杂的正则）
                if suffix in filename:
                    filenames.append(filename)

            # 按文件名排序（假设文件名包含时间戳）
            filenames.sort(reverse=True)

            # 限制数量
            max_num_files = max_num_files or len(filenames)
            filenames = filenames[:max_num_files]

            logger.info(f"找到 {len(filenames)} 个文件，按日期排序")

            # 返回完整的OSS路径
            result = []
            for filename in filenames:
                if object_dir:
                    full_path = f"{object_dir.rstrip('/')}/{filename}"
                else:
                    full_path = filename
                result.append(full_path)

            return result

        except Exception as e:
            logger.error(f"列出最新文件失败: {e}")
            return []

    def download_object_to_file(
        self,
        oss_file_path: str,
        local_file_path: str,
        replace: bool = True,
        make_dir: bool = True
    ) -> bool:
        """
        从OSS下载对象到本地文件（兼容性方法）

        Args:
            oss_file_path: OSS文件路径
            local_file_path: 本地文件路径
            replace: 是否替换已存在的文件
            make_dir: 是否创建目录

        Returns:
            下载是否成功
        """
        try:
            # 检查本地文件是否存在
            if not replace and os.path.exists(local_file_path):
                logger.warning(f"本地文件已存在: {local_file_path}")
                return False

            # 创建目录
            if make_dir:
                local_dir = os.path.dirname(local_file_path)
                if local_dir:
                    os.makedirs(local_dir, exist_ok=True)

            # 使用现有的download_file方法
            return self.download_file(oss_file_path, local_file_path)

        except Exception as e:
            logger.error(f"下载对象失败: {oss_file_path} -> {local_file_path}, 错误: {e}")
            return False

    def get_file_info(self, oss_file_path: str) -> Optional[Dict]:
        """
        获取OSS文件信息

        Args:
            oss_file_path: OSS文件路径

        Returns:
            文件信息字典
        """
        try:
            obj = self.bucket.get_object_meta(oss_file_path)

            return {
                'key': oss_file_path,
                'name': os.path.basename(oss_file_path),
                'size': obj.content_length,
                'last_modified': obj.last_modified,
                'etag': obj.etag,
                'content_type': obj.content_type
            }

        except oss2.exceptions.NoSuchKey:
            logger.warning(f"文件不存在: {oss_file_path}")
            return None
        except Exception as e:
            logger.error(f"获取文件信息失败: {oss_file_path}, 错误: {e}")
            return None
    
    def delete_file(self, oss_file_path: str) -> bool:
        """
        删除OSS文件
        
        Args:
            oss_file_path: OSS文件路径
            
        Returns:
            删除是否成功
        """
        try:
            self.bucket.delete_object(oss_file_path)
            logger.info(f"删除成功: {oss_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"删除文件失败: {oss_file_path}, 错误: {e}")
            return False


# 兼容性别名 - 保持与原始代码的兼容性
class SimpleOSSManager(OSSFileManager):
    """兼容性别名"""
    pass


if __name__ == "__main__":
    # 测试代码
    try:
        manager = OSSFileManager()
        print("✅ OSS file manager initialized successfully")
        
        # 测试列出文件
        files = manager.list_files("atlas_eval/submissions/", file_extension=".json")
        print(f"📁 Found {len(files)} submission files")
        
        for file_info in files[:3]:  # 只显示前3个
            print(f"  - {file_info['name']} ({file_info['size']} bytes)")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
