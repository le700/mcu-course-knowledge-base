#!/usr/bin/env python3
"""
八爪鱼记忆中枢 - 命令行接口 (CLI)

提供命令行方式管理项目、会话、记忆和统计信息的入口。
使用 argparse 实现子命令路由。

Usage:
    python -m octopus_hub.cli init
    python -m octopus_hub.cli project register <id> <name>
    python -m octopus_hub.cli project list
    python -m octopus_hub.cli project context <id>
    python -m octopus_hub.cli session start <project_id>
    python -m octopus_hub.cli session end <session_id>
    python -m octopus_hub.cli memory add <project_id> <content>
    python -m octopus_hub.cli memory search <project_id> <query>
    python -m octopus_hub.cli memory recent <project_id>
    python -m octopus_hub.cli stats
"""

import argparse
import json
import sys
import os

# 确保包路径正确
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from octopus_hub.models import MemoryType, SessionStatus
from octopus_hub.core import OctopusHub


def _get_hub(db_path: str = None) -> OctopusHub:
    """获取 OctopusHub 实例

    Args:
        db_path: 数据库路径，默认使用标准路径

    Returns:
        OctopusHub: 中枢实例
    """
    if db_path is None:
        db_path = "/workspace/octopus_hub/hub.db"
    return OctopusHub(storage_path=db_path)


def _print_json(data):
    """格式化打印 JSON 数据"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_init(args):
    """初始化八爪鱼中枢"""
    hub = _get_hub(args.db)
    stats = hub.get_stats()
    print("八爪鱼记忆中枢初始化完成!")
    print(f"  数据库路径: {args.db}")
    print(f"  现有项目数: {stats.get('projects', 0)}")
    print(f"  现有记忆数: {stats.get('memories', 0)}")
    print(f"  现有会话数: {stats.get('sessions', 0)}")
    hub.close()


def cmd_project_register(args):
    """注册新项目"""
    hub = _get_hub(args.db)
    try:
        project = hub.register_project(
            project_id=args.id,
            project_name=args.name,
            workspace_path=args.path or ""
        )
        print(f"项目注册成功: {project.project_id}")
        print(f"  名称: {project.project_name}")
        print(f"  工作区: {project.workspace_path}")
        print(f"  自动创建人格: persona_{project.project_id}")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
    finally:
        hub.close()


def cmd_project_list(args):
    """列出所有项目"""
    hub = _get_hub(args.db)
    try:
        projects = hub.list_projects()
        if not projects:
            print("暂无项目")
            return
        print(f"共有 {len(projects)} 个项目:\n")
        for p in projects:
            active = " [活跃]" if p.active_session_id else ""
            print(f"  [{p.project_id}] {p.project_name}{active}")
            print(f"      状态: {p.status} | 工作区: {p.workspace_path or '未设置'}")
            print(f"      创建: {p.created_at} | 更新: {p.updated_at}")
            print()
    finally:
        hub.close()


def cmd_project_context(args):
    """显示项目上下文"""
    hub = _get_hub(args.db)
    try:
        context = hub.get_project_context(args.id)
        if "error" in context:
            print(f"错误: {context['error']}")
            sys.exit(1)
        _print_json(context)
    finally:
        hub.close()


def cmd_session_start(args):
    """开始新会话"""
    hub = _get_hub(args.db)
    try:
        session = hub.start_session(args.project_id, agent_id=args.agent or "unknown")
        print(f"会话已开始: {session.session_id}")
        print(f"  项目: {session.project_id}")
        print(f"  Agent: {session.agent_id}")
        print(f"  状态: {session.status.value}")
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)
    finally:
        hub.close()


def cmd_session_end(args):
    """结束会话"""
    hub = _get_hub(args.db)
    try:
        session = hub.end_session(args.session_id)
        if session:
            print(f"会话已结束: {session.session_id}")
            print(f"  状态: {session.status.value}")
            print(f"  结束时间: {session.ended_at}")
        else:
            print(f"错误: 会话 {args.session_id} 不存在")
            sys.exit(1)
    finally:
        hub.close()


def cmd_memory_add(args):
    """添加记忆"""
    hub = _get_hub(args.db)
    try:
        # 解析记忆类型
        mem_type = MemoryType(args.type) if args.type else MemoryType.INSIGHT

        # 解析标签
        tags = []
        if args.tags:
            tags = [t.strip() for t in args.tags.split(",") if t.strip()]

        # 解析重要性
        importance = float(args.importance) if args.importance else 0.5

        memory = hub.add_memory(
            project_id=args.project_id,
            content=args.content,
            memory_type=mem_type,
            importance=importance,
            tags=tags
        )
        print(f"记忆已添加: {memory.memory_id}")
        print(f"  类型: {memory.memory_type.value}")
        print(f"  重要性: {memory.importance}")
        print(f"  标签: {', '.join(memory.tags) if memory.tags else '无'}")
        print(f"  内容: {memory.content[:100]}{'...' if len(memory.content) > 100 else ''}")
    except ValueError as e:
        print(f"错误: 无效的记忆类型 '{args.type}'，可选: {[t.value for t in MemoryType]}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
    finally:
        hub.close()


def cmd_memory_search(args):
    """搜索记忆"""
    hub = _get_hub(args.db)
    try:
        mem_type = MemoryType(args.type) if args.type else None
        memories = hub.search_memories(
            project_id=args.project_id,
            query=args.query,
            memory_type=mem_type,
            limit=args.limit or 10
        )
        if not memories:
            print(f"未找到匹配 '{args.query}' 的记忆")
            return
        print(f"找到 {len(memories)} 条匹配记忆:\n")
        for m in memories:
            print(f"  [{m.memory_id}] ({m.memory_type.value}) 重要性: {m.importance}")
            print(f"  内容: {m.content[:120]}{'...' if len(m.content) > 120 else ''}")
            print(f"  标签: {', '.join(m.tags) if m.tags else '无'}")
            print()
    except ValueError:
        print(f"错误: 无效的记忆类型 '{args.type}'")
        sys.exit(1)
    finally:
        hub.close()


def cmd_memory_recent(args):
    """显示最近记忆"""
    hub = _get_hub(args.db)
    try:
        memories = hub.get_recent_memories(args.project_id, limit=args.limit or 20)
        if not memories:
            print(f"项目 {args.project_id} 暂无记忆")
            return
        print(f"项目 {args.project_id} 最近 {len(memories)} 条记忆:\n")
        for m in memories:
            print(f"  [{m.memory_id}] ({m.memory_type.value}) 重要性: {m.importance}")
            print(f"  内容: {m.content[:120]}{'...' if len(m.content) > 120 else ''}")
            print(f"  标签: {', '.join(m.tags) if m.tags else '无'}")
            print()
    finally:
        hub.close()


def cmd_stats(args):
    """显示统计信息"""
    hub = _get_hub(args.db)
    try:
        stats = hub.get_stats()
        print("八爪鱼记忆中枢 - 统计信息")
        print("=" * 40)
        print(f"  项目数: {stats.get('projects', 0)}")
        print(f"  记忆数: {stats.get('memories', 0)}")
        print(f"  会话数: {stats.get('sessions', 0)}")
        print(f"  人格数: {stats.get('personas', 0)}")
        print("=" * 40)
    finally:
        hub.close()


def main():
    """CLI 主入口"""
    parser = argparse.ArgumentParser(
        description="八爪鱼记忆中枢 (Octopus Hub) - 命令行管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s init
  %(prog)s project register my_proj "我的项目" --path /workspace/my_project
  %(prog)s project list
  %(prog)s project context my_proj
  %(prog)s session start my_proj --agent claude
  %(prog)s session end sess_my_proj_1234567890
  %(prog)s memory add my_proj "修复了数据库连接池泄漏" --type error_fix --importance 0.8
  %(prog)s memory search my_proj "数据库"
  %(prog)s memory recent my_proj
  %(prog)s stats
        """
    )

    # 全局参数
    parser.add_argument("--db", default="/workspace/octopus_hub/hub.db",
                        help="数据库文件路径 (默认: /workspace/octopus_hub/hub.db)")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # ---- init ----
    p_init = subparsers.add_parser("init", help="初始化八爪鱼中枢")
    p_init.set_defaults(func=cmd_init)

    # ---- project ----
    p_project = subparsers.add_parser("project", help="项目管理")
    p_project_sub = p_project.add_subparsers(dest="subcommand")

    p_register = p_project_sub.add_parser("register", help="注册新项目")
    p_register.add_argument("id", help="项目 ID")
    p_register.add_argument("name", help="项目名称")
    p_register.add_argument("--path", help="工作区路径")
    p_register.set_defaults(func=cmd_project_register)

    p_list = p_project_sub.add_parser("list", help="列出所有项目")
    p_list.set_defaults(func=cmd_project_list)

    p_context = p_project_sub.add_parser("context", help="显示项目上下文")
    p_context.add_argument("id", help="项目 ID")
    p_context.set_defaults(func=cmd_project_context)

    # ---- session ----
    p_session = subparsers.add_parser("session", help="会话管理")
    p_session_sub = p_session.add_subparsers(dest="subcommand")

    p_s_start = p_session_sub.add_parser("start", help="开始新会话")
    p_s_start.add_argument("project_id", help="项目 ID")
    p_s_start.add_argument("--agent", help="Agent 标识")
    p_s_start.set_defaults(func=cmd_session_start)

    p_s_end = p_session_sub.add_parser("end", help="结束会话")
    p_s_end.add_argument("session_id", help="会话 ID")
    p_s_end.set_defaults(func=cmd_session_end)

    # ---- memory ----
    p_memory = subparsers.add_parser("memory", help="记忆管理")
    p_memory_sub = p_memory.add_subparsers(dest="subcommand")

    p_m_add = p_memory_sub.add_parser("add", help="添加记忆")
    p_m_add.add_argument("project_id", help="项目 ID")
    p_m_add.add_argument("content", help="记忆内容")
    p_m_add.add_argument("--type", default="insight",
                         choices=[t.value for t in MemoryType],
                         help="记忆类型")
    p_m_add.add_argument("--importance", type=float, default=0.5,
                         help="重要性评分 (0.0~1.0)")
    p_m_add.add_argument("--tags", help="标签，逗号分隔")
    p_m_add.set_defaults(func=cmd_memory_add)

    p_m_search = p_memory_sub.add_parser("search", help="搜索记忆")
    p_m_search.add_argument("project_id", help="项目 ID")
    p_m_search.add_argument("query", help="搜索关键词")
    p_m_search.add_argument("--type", choices=[t.value for t in MemoryType],
                            help="按类型过滤")
    p_m_search.add_argument("--limit", type=int, default=10,
                            help="返回数量上限")
    p_m_search.set_defaults(func=cmd_memory_search)

    p_m_recent = p_memory_sub.add_parser("recent", help="最近记忆")
    p_m_recent.add_argument("project_id", help="项目 ID")
    p_m_recent.add_argument("--limit", type=int, default=20,
                            help="返回数量上限")
    p_m_recent.set_defaults(func=cmd_memory_recent)

    # ---- stats ----
    p_stats = subparsers.add_parser("stats", help="显示统计信息")
    p_stats.set_defaults(func=cmd_stats)

    # 解析并执行
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()