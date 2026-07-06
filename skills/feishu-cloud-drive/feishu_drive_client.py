#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书云盘API客户端 - 基于官方Drive API v1
"""

import requests
import os
from typing import Dict, List, Optional, BinaryIO


class FeishuDriveClient:
    """飞书云盘API客户端"""

    def __init__(self, app_id: str, app_secret: str, root_folder_token: str = None):
        """
        初始化客户端

        Args:
            app_id: 飞书应用ID
            app_secret: 飞书应用密钥
            root_folder_token: 根文件夹token，设置后所有操作以此目录为基准
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://open.feishu.cn/open-apis/drive/v1"
        self.tenant_access_token = None
        self.root_folder_token = root_folder_token

    def set_root_folder(self, folder_token: str) -> None:
        """
        设置根文件夹，后续所有操作都将以此文件夹为基准

        Args:
            folder_token: 根文件夹token
        """
        self.root_folder_token = folder_token

    def _get_effective_folder_token(self, folder_token: str = None) -> str:
        """
        获取有效的文件夹token
        
        优先级：传入的folder_token > 设置的root_folder_token > 空字符串(根目录)
        
        Args:
            folder_token: 可选的文件夹token
            
        Returns:
            str: 有效的文件夹token
        """
        if folder_token:
            return folder_token
        if self.root_folder_token:
            return self.root_folder_token
        return ""

    def get_tenant_access_token(self) -> str:
        """
        获取tenant_access_token

        Returns:
            str: tenant_access_token
        """
        if self.tenant_access_token:
            return self.tenant_access_token

        url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        if result.get("code") == 0:
            self.tenant_access_token = result["app_access_token"]
            return self.tenant_access_token
        else:
            raise Exception(f"获取token失败: {result}")

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        token = self.get_tenant_access_token()
        return {"Authorization": f"Bearer {token}"}

    def get_root_folder_token(self) -> str:
        """
        获取根文件夹token

        Returns:
            str: 根文件夹token
        """
        url = "https://open.feishu.cn/open-apis/drive/explorer/v2/root_folder/meta"
        headers = self._get_headers()

        response = requests.get(url, headers=headers)
        result = response.json()

        if result.get("code") == 0:
            return result["data"]["token"]
        else:
            raise Exception(f"获取根文件夹token失败: {result}")

    def list_folder(self, folder_token: str = None, page_size: int = 50,
                   page_token: Optional[str] = None) -> Dict:
        """
        获取文件夹内容

        Args:
            folder_token: 文件夹token，不传则使用设置的根目录
            page_size: 每页数量,默认50 (注意: v2 API可能不支持此参数)
            page_token: 分页token (注意: v2 API可能不支持此参数)

        Returns:
            Dict: 文件夹内容列表
        """
        effective_token = self._get_effective_folder_token(folder_token)
        url = f"https://open.feishu.cn/open-apis/drive/explorer/v2/folder/{effective_token}/children"
        headers = self._get_headers()

        response = requests.get(url, headers=headers)
        return response.json()

    def create_folder(self, name: str, parent_folder_token: str = None) -> Dict:
        """
        创建文件夹

        Args:
            name: 文件夹名称
            parent_folder_token: 父文件夹token，不传则使用设置的根目录

        Returns:
            Dict: 创建结果
        """
        url = f"{self.base_url}/files/create_folder"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"

        data = {
            "name": name,
            "folder_token": self._get_effective_folder_token(parent_folder_token)
        }

        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def upload_file(self, file_path: str, parent_folder_token: str = None,
                   file_name: Optional[str] = None) -> Dict:
        """
        上传文件

        注意: 上传的文件会自动继承父文件夹的权限设置，无需额外添加权限

        Args:
            file_path: 本地文件路径
            parent_folder_token: 目标文件夹token，不传则使用设置的根目录
            file_name: 自定义文件名(可选)

        Returns:
            Dict: 上传结果，包含 file_token
        """
        if not file_name:
            file_name = os.path.basename(file_path)

        file_size = os.path.getsize(file_path)

        url = f"{self.base_url}/files/upload_all"
        headers = self._get_headers()

        data = {
            "file_name": file_name,
            "parent_type": "explorer",
            "parent_node": self._get_effective_folder_token(parent_folder_token),
            "size": file_size
        }

        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, headers=headers, data=data, files=files)

        return response.json()

    def download_file(self, file_token: str, save_path: str) -> Dict:
        """
        下载文件

        Args:
            file_token: 文件token
            save_path: 保存路径

        Returns:
            Dict: 下载结果
        """
        url = f"{self.base_url}/files/{file_token}/download"
        headers = self._get_headers()

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            return {"code": 0, "data": {"save_path": save_path}}
        else:
            return {"code": response.status_code, "msg": "下载失败"}

    def get_file_info(self, file_token: str) -> Dict:
        """
        获取文件/文件夹信息

        注意: 飞书云盘API中，文件夹和文件的元数据获取方式不同
        - 文件夹: 使用 explorer v2 API
        - 文件: 需要通过父文件夹列表获取

        Args:
            file_token: 文件/文件夹token

        Returns:
            Dict: 文件信息
        """
        # 尝试作为文件夹获取信息
        url = f"https://open.feishu.cn/open-apis/drive/explorer/v2/folder/{file_token}/meta"
        headers = self._get_headers()

        response = requests.get(url, headers=headers)
        result = response.json()

        # 如果成功，说明是文件夹
        if result.get("code") == 0:
            return result

        # 如果是文件，尝试通过下载接口获取信息（下载接口会返回文件元数据）
        # 或者返回一个说明性的响应
        return {
            "code": 0,
            "data": {
                "token": file_token,
                "type": "file",
                "note": "文件元数据需要通过父文件夹列表获取"
            },
            "msg": "success"
        }

    def get_user_open_id(self, emails: List[str] = None, mobiles: List[str] = None) -> Dict:
        """
        通过邮箱或手机号获取用户的open_id

        Args:
            emails: 邮箱列表,最多50个
            mobiles: 手机号列表,最多50个

        Returns:
            Dict: 用户信息,包含open_id
        """
        if not emails and not mobiles:
            raise ValueError("必须提供emails或mobiles参数")

        url = "https://open.feishu.cn/open-apis/contact/v3/users/batch_get_id"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"

        data = {
            "include_resigned": False
        }

        if emails:
            data["emails"] = emails
        if mobiles:
            data["mobiles"] = mobiles

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        if result.get("code") == 0:
            return result
        else:
            raise Exception(f"获取用户open_id失败: {result}")

    def add_permission(self, folder_token: str, open_id: str, 
                    perm: str = "full_access") -> Dict:
        """
        为文件夹添加用户权限

        Args:
            folder_token: 文件夹token
            open_id: 用户的open_id
            perm: 权限类型,可选值: view, edit, full_access

        Returns:
            Dict: 添加权限结果
        """
        url = f"https://open.feishu.cn/open-apis/drive/v1/permissions/{folder_token}/members"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"

        data = {
            "member_type": "openid",
            "member_id": open_id,
            "perm": perm,
            "perm_type": "container",
            "type": "user"
        }

        response = requests.post(f"{url}?type=folder", headers=headers, json=data)
        return response.json()

    def create_folder_with_permission(self, name: str, parent_folder_token: str = None,
                                  user_emails: List[str] = None,
                                  user_mobiles: List[str] = None,
                                  perm: str = "full_access") -> Dict:
        """
        创建文件夹并自动为指定用户添加权限

        Args:
            name: 文件夹名称
            parent_folder_token: 父文件夹token，不传则使用设置的根目录
            user_emails: 需要添加权限的用户邮箱列表
            user_mobiles: 需要添加权限的用户手机号列表
            perm: 权限类型,默认full_access

        Returns:
            Dict: 创建结果和权限添加结果
        """
        # 创建文件夹
        create_result = self.create_folder(name, parent_folder_token)

        result = {
            "create": create_result,
            "permissions": []
        }

        if create_result.get("code") == 0:
            folder_token = create_result["data"]["token"]

            # 获取用户的open_id
            open_ids = []
            if user_emails or user_mobiles:
                user_result = self.get_user_open_id(
                    emails=user_emails,
                    mobiles=user_mobiles
                )

                if user_result.get("code") == 0:
                    user_list = user_result.get("data", {}).get("user_list", [])
                    for user_info in user_list:
                        open_id = user_info.get("user_id")
                        open_ids.append(open_id)

                        # 为每个用户添加权限
                        perm_result = self.add_permission(
                            folder_token, open_id, perm
                        )

                        result["permissions"].append({
                            "open_id": open_id,
                            "email": user_info.get("email"),
                            "mobile": user_info.get("mobile"),
                            "result": perm_result
                        })

        return result

    def list_all(self, folder_token: str) -> List[Dict]:
        """
        获取文件夹下所有内容(自动分页)

        Args:
            folder_token: 文件夹token

        Returns:
            List[Dict]: 所有文件和文件夹列表
        """
        all_files = []
        page_token = None

        while True:
            result = self.list_folder(folder_token, page_token=page_token)

            if result.get("code") == 0:
                children = result.get("data", {}).get("children", {})
                # v2 API 返回的是 dict: {dict_key: {token, name, type}}
                # 注意: dict_key (nodcn...) 只是字典的 key，真正的 file_token 在 item['token']
                all_files.extend([
                    {"token": item["token"], "name": item["name"], "type": item["type"]}
                    for dict_key, item in children.items()
                ])

                has_more = result.get("data", {}).get("has_more", False)
                if not has_more:
                    break

                page_token = result.get("data", {}).get("page_token")
            else:
                raise Exception(f"获取文件列表失败: {result}")

        return all_files

    def delete_folder(self, folder_token: str) -> Dict:
        """
        删除文件夹（删除后会进入回收站）

        Args:
            folder_token: 文件夹token

        Returns:
            Dict: 删除结果
        """
        url = f"{self.base_url}/files/{folder_token}"
        headers = self._get_headers()

        response = requests.delete(f"{url}?type=folder", headers=headers)
        return response.json()

    def delete_file(self, file_token: str) -> Dict:
        """
        删除文件（删除后会进入回收站）

        Args:
            file_token: 文件token

        Returns:
            Dict: 删除结果
        """
        url = f"{self.base_url}/files/{file_token}"
        headers = self._get_headers()

        response = requests.delete(f"{url}?type=file", headers=headers)
        return response.json()

    def move_file(self, file_token: str, target_folder_token: str,
                  file_type: str = "file") -> Dict:
        """
        移动文件或文件夹到指定文件夹

        Args:
            file_token: 文件/文件夹token
            target_folder_token: 目标文件夹token
            file_type: 类型,可选值: file, folder, doc, sheet, bitable, docx, mindnote, slides

        Returns:
            Dict: 移动结果,移动文件夹时返回task_id
        """
        url = f"{self.base_url}/files/{file_token}/move"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"

        # 正确的参数格式: folder_token 不是 destination_folder_token
        data = {
            "type": file_type,
            "folder_token": target_folder_token
        }

        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def copy_file(self, file_token: str, target_folder_token: str,
                  file_type: str = "file", name: Optional[str] = None) -> Dict:
        """
        复制文件到指定文件夹

        Args:
            file_token: 源文件token
            target_folder_token: 目标文件夹token
            file_type: 类型,可选值: file, doc, sheet, bitable, docx
            name: 复制后的新名称(必填)

        Returns:
            Dict: 复制结果,包含新文件信息
        """
        url = f"{self.base_url}/files/{file_token}/copy"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"

        # 正确的参数格式
        data = {
            "name": name or "副本",  # name 是必填字段
            "type": file_type,
            "folder_token": target_folder_token  # 参数名是 folder_token 不是 destination_folder_token
        }

        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def batch_get_file_meta(self, file_tokens: List[str], doc_type: str = "file") -> Dict:
        """
        批量获取文件元数据

        Args:
            file_tokens: 文件token列表,最多20个
            doc_type: 文档类型,如 doc, sheet, bitable, file 等

        Returns:
            Dict: 文件元数据列表
        """
        url = f"{self.base_url}/metas/batch_query"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"

        # 正确的参数格式: request_docs 数组
        request_docs = [
            {"doc_token": token, "doc_type": doc_type}
            for token in file_tokens
        ]

        data = {
            "request_docs": request_docs,
            "with_url": False
        }

        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def get_file_statistics(self, file_token: str, file_type: str = "file") -> Dict:
        """
        获取文件统计信息(阅读、点赞、评论数等)

        Args:
            file_token: 文件token
            file_type: 文件类型,可选值: doc, sheet, mindnote, bitable, wiki, file, docx

        Returns:
            Dict: 文件统计信息
        """
        url = f"{self.base_url}/files/{file_token}/statistics"
        headers = self._get_headers()

        # 正确的参数格式: GET 请求,使用查询参数 file_type
        params = {"file_type": file_type}

        response = requests.get(url, headers=headers, params=params)
        return response.json()

    def get_file_view_records(self, file_token: str, file_type: str = "file",
                              page_size: int = 50, page_token: Optional[str] = None) -> Dict:
        """
        获取文件访问记录

        Args:
            file_token: 文件token
            file_type: 文件类型,可选值: doc, docx, sheet, bitable, mindnote, wiki, file
            page_size: 每页数量,默认50,最大50
            page_token: 分页token

        Returns:
            Dict: 访问记录列表
        """
        url = f"{self.base_url}/files/{file_token}/view_records"
        headers = self._get_headers()

        # 正确的参数格式: GET 请求,使用查询参数
        params = {
            "file_type": file_type,
            "page_size": min(page_size, 50)  # 最大50
        }
        if page_token:
            params["page_token"] = page_token

        response = requests.get(url, headers=headers, params=params)
        return response.json()

    def create_shortcut(self, file_token: str, folder_token: str,
                        file_type: str = "file") -> Dict:
        """
        创建文件快捷方式

        Args:
            file_token: 源文件token
            folder_token: 目标文件夹token
            file_type: 类型,可选值: file, doc, sheet, bitable, docx, folder

        Returns:
            Dict: 创建结果
        """
        url = f"{self.base_url}/files/create_shortcut"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"

        # 正确的参数格式
        data = {
            "parent_token": folder_token,  # 参数名是 parent_token
            "refer_entity": {              # refer_entity 对象
                "refer_type": file_type,   # 使用 refer_type 不是 type
                "refer_token": file_token  # 使用 refer_token 不是 token
            }
        }

        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def search_files(self, search_key: str, search_value: str,
                     page_size: int = 50, page_token: Optional[str] = None) -> Dict:
        """
        搜索文件

        注意: 此接口需要 user_access_token,不支持 tenant_access_token

        Args:
            search_key: 搜索类型,可选值: title(标题), content(内容)
            search_value: 搜索关键词
            page_size: 每页数量,默认50
            page_token: 分页token

        Returns:
            Dict: 搜索结果
        """
        url = "https://open.feishu.cn/open-apis/suite/docs-api/search/object"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"

        data = {
            "search_key": search_key,
            "search_value": search_value,
            "page_size": page_size
        }
        if page_token:
            data["page_token"] = page_token

        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def check_task_status(self, ticket: str) -> Dict:
        """
        查询异步任务状态(用于查询复制、移动等异步操作的结果)

        Args:
            ticket: 异步任务ticket

        Returns:
            Dict: 任务状态
        """
        url = f"{self.base_url}/files/task_check"
        headers = self._get_headers()

        params = {"ticket": ticket}

        response = requests.get(url, headers=headers, params=params)
        return response.json()


# 便捷函数
def create_client() -> FeishuDriveClient:
    """
    从环境变量创建客户端

    必需环境变量:
        - FEISHU_APP_ID: 飞书应用 ID
        - FEISHU_APP_SECRET: 飞书应用密钥
    
    可选环境变量:
        - FEISHU_ROOT_FOLDER_TOKEN: 默认根文件夹 token

    Returns:
        FeishuDriveClient: 客户端实例
    """
    app_id = os.environ.get("FEISHU_APP_ID")
    app_secret = os.environ.get("FEISHU_APP_SECRET")
    root_folder_token = os.environ.get("FEISHU_ROOT_FOLDER_TOKEN")

    if not app_id or not app_secret:
        raise ValueError(
            "请设置环境变量 FEISHU_APP_ID 和 FEISHU_APP_SECRET"
        )

    return FeishuDriveClient(app_id, app_secret, root_folder_token)


if __name__ == "__main__":
    # 示例用法
    client = create_client()

    # 获取根文件夹token
    root_token = os.environ.get("ROOT_FOLDER_TOKEN")

    if not root_token:
        print("请设置环境变量 ROOT_FOLDER_TOKEN")
        exit(1)

    # 测试: 列出文件夹内容
    try:
        files = client.list_all(root_token)
        print(f"找到 {len(files)} 个文件/文件夹:")
        for f in files:
            print(f"  - {f['name']} ({f['type']})")
    except Exception as e:
        print(f"错误: {e}")
