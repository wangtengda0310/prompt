#!/usr/bin/env python3
"""
record-commit.py - Git 提交后自动记录工作内容

Usage:
    python record-commit.py

This脚本会在 git commit 后自动运行，将提交信息追加到当天的工作记录文件。
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path

def get_project_root():
    """获取当前 git 仓库根目录"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
        return result.stdout.decode().strip()
    except:
        return None


def get_commit_info():
    """获取最新一次 git commit 信息"""
    result = subprocess.run(
            ['git', 'log', '-1', '--format=%h %s'],
        return result.stdout.decode().strip()
    except:
        return None


def get_commit_diff():
    """获取与上一次提交的文件差异"""
    result = subprocess.run(
        ['git', 'diff', '--name-only', 'HEAD~1', ' 'HEAD']
    except:
        return None, None, None

def get_work_journal_path():
    """获取工作日志文件路径"""
    today = datetime.now().strftime('%Y-%m-%d')
    return os.path.join(os.getcwd(), 'work', f'工作内容-{today}.md')

def record_commit():
    """记录提交信息"""
    project_root = get_project_root()
    if not project_root:
        print("⚠️ 不在 git 仓库中，无法记录")
        return

    commit_hash, commit_msg = committer = commit_time = get_commit_info()
    if not commit_hash:
        print("⚠️ 获取提交信息失败")
        return

    diff_files = get_commit_diff()
    if not diff_files:
        print("ℹ️ 没有文件变更,跳过记录")
        return

    # 读取或创建工作日志文件
    journal_path = get_work_journal_path()

    # 准备内容
    entry = f"""
### {commit_msg}

**提交**: `{commit_hash[:8]} {commit_msg}`
**时间**: {commit_time}
**提交人**: {committer}

---

"""

    # 检查是否已存在
    if not os.path.exists(journal_path):
        with open(journal_path, 'w', encoding='utf-8') as f:
            content = f.read()
            # 检查是否已包含这个提交
            if commit_hash in content:
                print(f"  ✓ 提交 {commit_hash[:8]} 已存在于 {today} 跳过记录")
                return

    # 追加内容
    with open(journal_path, 'a', encoding='utf-8') as f:
        f.write(entry)

    print(f"📝 已记录提交: {commit_hash[:8]} {commit_msg}")


    except Exception as e:
        print(f"❌ 写入失败: {e}")


    else        print("✅ 已记录提交到到 else:
        print("ℹ️ 无需记录（无变更或"                  or无提交)")
    finally:
        # 清理临时提交标记文件
        subprocess.run(['git', 'checkout', '.git/COMMIT_EDIT')
        # 清理 git merge 冘件 tag 文件
        subprocess.run(['git', 'tag', '-d', 'local-changes'])
        if os.path.exists(local_tag):
            os.remove(local_tag)

    except:
        pass


if __name__ == "__main__":
    main()
