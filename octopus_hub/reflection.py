import time
import json
from typing import List, Dict, Optional, Tuple
from .models import MemoryFragment, MemoryType, Session, SessionStatus, Persona

# 可选依赖：jieba 用于 TF-IDF 中文分词，不可用时回退到简单分词
try:
    import jieba
    _JIEBA_AVAILABLE = True
except ImportError:
    _JIEBA_AVAILABLE = False

# 可选依赖：sklearn 用于 TF-IDF 向量化，不可用时回退到规则引擎
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    import numpy as np
    _TFIDF_AVAILABLE = True
except ImportError:
    _TFIDF_AVAILABLE = False


class ReflectionEngine:
    """反思引擎 - 会话结束后的记忆提炼与反思"""

    def __init__(self, storage=None):
        """
        Args:
            storage: HubStorage 实例
        """
        self.storage = storage

    def reflect_on_session(self, session_id: str,
                           messages: List[Dict] = None,
                           use_llm: bool = False,
                           vector_store=None) -> dict:
        """
        对会话进行反思提炼

        Args:
            session_id: 会话ID
            messages: 会话消息列表 [{"role": "user/assistant", "content": "..."}]
            use_llm: 是否使用本地LLM做提炼（暂用规则引擎代替）

        Returns:
            {
                "session_id": str,
                "memories_created": int,
                "persona_updated": bool,
                "reflection_summary": str
            }
        """
        session = self.storage.get_session(session_id)
        if not session:
            return {"error": f"会话 {session_id} 不存在"}

        if not messages:
            messages = []

        result = {
            "session_id": session_id,
            "memories_created": 0,
            "persona_updated": False,
            "reflection_summary": "",
            "extracted": {
                "decisions": [],
                "errors": [],
                "insights": [],
                "preferences": []
            }
        }

        # 1. TF-IDF 关键句提取
        tfidf_sentences = self._tfidf_extract_key_sentences(messages, top_n=10)
        tfidf_extracted = {"decisions": [], "errors": [], "insights": [], "preferences": []}
        for sentence in tfidf_sentences:
            category = self._classify_sentence(sentence)
            if category == "decision":
                tfidf_extracted["decisions"].append(sentence[:300])
            elif category == "error":
                tfidf_extracted["errors"].append(sentence[:300])
            elif category == "insight":
                tfidf_extracted["insights"].append(sentence[:300])
            elif category == "preference":
                tfidf_extracted["preferences"].append(sentence[:300])

        # 提取关键信息（规则引擎）
        if use_llm:
            extracted = self._llm_extract(messages)
        else:
            extracted = self._rule_extract(messages)

        # 合并 TF-IDF 和规则引擎的结果并去重
        for key in ["decisions", "errors", "insights", "preferences"]:
            combined = list(set(extracted.get(key, []) + tfidf_extracted.get(key, [])))
            extracted[key] = combined[:8]

        # 使用向量存储去重（检查新记忆是否与已有记忆重复）
        if vector_store is not None:
            for key in ["decisions", "errors", "insights", "preferences"]:
                try:
                    items = extracted.get(key, [])
                    filtered = [item for item in items if not vector_store.deduplicate(item)]
                    extracted[key] = filtered
                except Exception:
                    pass

        result["extracted"] = extracted

        # 2. 创建记忆碎片
        project_id = session.project_id
        memories_created = []

        for decision in extracted.get("decisions", []):
            mem = self._create_memory(project_id, session_id, decision,
                                       MemoryType.DECISION, importance=0.8)
            memories_created.append(mem)

        for error_fix in extracted.get("errors", []):
            mem = self._create_memory(project_id, session_id, error_fix,
                                       MemoryType.ERROR_FIX, importance=0.9)
            memories_created.append(mem)

        for insight in extracted.get("insights", []):
            mem = self._create_memory(project_id, session_id, insight,
                                       MemoryType.INSIGHT, importance=0.6)
            memories_created.append(mem)

        result["memories_created"] = len(memories_created)

        # 3. 更新人格（检测偏好变化）
        if extracted.get("preferences"):
            persona_updated = self._update_persona_from_reflection(
                project_id, extracted["preferences"])
            result["persona_updated"] = persona_updated

        # 4. 生成反思摘要
        result["reflection_summary"] = self._generate_summary(
            session, extracted, len(memories_created))

        # 5. 更新会话状态
        session.status = SessionStatus.COMPLETED
        session.refinement_status = "completed"
        session.refined_memories = [m.memory_id for m in memories_created]
        self.storage.update_session(session)

        return result

    def _tfidf_extract_key_sentences(self, messages: List[Dict], top_n: int = 5) -> List[str]:
        """
        使用 TF-IDF 提取对话中最关键的句子。

        流程：
        1. 将 messages 按句子分割（用 。！？\n 断句）
        2. 过滤太短的句子（< 10 字）
        3. 用 jieba 分词后构建 TF-IDF 矩阵
        4. 计算每个句子的 TF-IDF 平均分
        5. 返回 top_n 个最高分句子
        """
        import re

        # 1. 拼接所有消息内容并按句子分割
        all_text = " ".join([msg.get("content", "") for msg in messages])
        sentences = re.split(r'[。！？\n]+', all_text)
        sentences = [s.strip() for s in sentences if len(s.strip()) >= 10]

        if len(sentences) < 2:
            return sentences[:top_n]

        # 2. 用 jieba 分词
        try:
            segmented = [" ".join(jieba.cut(s)) for s in sentences]
        except Exception:
            return sentences[:top_n]

        # 3. 构建 TF-IDF 矩阵
        try:
            vectorizer = TfidfVectorizer(max_features=100, token_pattern=r'(?u)\b\w+\b')
            tfidf_matrix = vectorizer.fit_transform(segmented)

            # 4. 计算每个句子的平均 TF-IDF 分数
            scores = np.array(tfidf_matrix.mean(axis=1)).flatten()

            # 5. 取 top_n
            top_indices = np.argsort(scores)[-top_n:][::-1]
            return [sentences[i] for i in top_indices]
        except Exception:
            return sentences[:top_n]

    def _classify_sentence(self, sentence: str) -> str:
        """
        分类句子类型。
        返回："decision" | "error" | "insight" | "preference" | "none"

        优先级：error > preference > decision > insight > none
        使用 _rule_extract 中已有的关键词列表
        """
        # 错误修正关键词（优先级最高）
        error_keywords = ["错误", "不对", "bug", "修正", "修复", "搞错了", "不是",
                          "应该是", "改正", "更正", "纠正"]
        # 偏好关键词
        preference_keywords = ["更喜欢", "以后都用", "不如", "换成", "偏好", "习惯",
                               "倾向于", "不喜欢", "别用", "不要用"]
        # 决策关键词
        decision_keywords = ["就按", "确定", "改成", "方案", "决定", "采用", "选择",
                             "最终", "就这样", "用这个", "选这个"]
        # 洞察关键词
        insight_keywords = ["原来", "发现", "经验", "记住", "注意", "关键", "重点",
                            "学到了", "了解", "明白了"]

        # 按优先级检查：error > preference > decision > insight > none
        for kw in error_keywords:
            if kw in sentence:
                return "error"
        for kw in preference_keywords:
            if kw in sentence:
                return "preference"
        for kw in decision_keywords:
            if kw in sentence:
                return "decision"
        for kw in insight_keywords:
            if kw in sentence:
                return "insight"
        return "none"

    def _rule_extract(self, messages: List[Dict]) -> dict:
        """
        基于规则的关键信息提取（不依赖LLM）

        识别模式：
        - 决策：包含"就按"、"确定"、"改成"、"方案"、"决定"等
        - 错误：包含"错误"、"不对"、"bug"、"修正"、"修复"等
        - 洞察：包含"原来"、"发现"、"经验"、"记住"等
        - 偏好：包含"更喜欢"、"以后都用"、"不如"、"换成"等
        """
        decisions = []
        errors = []
        insights = []
        preferences = []

        # 决策关键词
        decision_keywords = ["就按", "确定", "改成", "方案", "决定", "采用", "选择",
                             "最终", "就这样", "用这个", "选这个"]
        # 错误修正关键词
        error_keywords = ["错误", "不对", "bug", "修正", "修复", "搞错了", "不是",
                          "应该是", "改正", "更正", "纠正"]
        # 洞察关键词
        insight_keywords = ["原来", "发现", "经验", "记住", "注意", "关键", "重点",
                            "学到了", "了解", "明白了"]
        # 偏好关键词
        preference_keywords = ["更喜欢", "以后都用", "不如", "换成", "偏好", "习惯",
                               "倾向于", "不喜欢", "别用", "不要用"]

        for msg in messages:
            content = msg.get("content", "")
            role = msg.get("role", "")

            if role == "user":
                for kw in decision_keywords:
                    if kw in content:
                        decisions.append(content[:300])
                        break
                for kw in preference_keywords:
                    if kw in content:
                        preferences.append(content[:300])
                        break
                for kw in error_keywords:
                    if kw in content:
                        errors.append(content[:300])
                        break

            # 洞察来自双方
            for kw in insight_keywords:
                if kw in content:
                    insights.append(content[:300])
                    break

        # 去重并限制数量
        return {
            "decisions": list(set(decisions))[:5],
            "errors": list(set(errors))[:5],
            "insights": list(set(insights))[:5],
            "preferences": list(set(preferences))[:5]
        }

    def _llm_extract(self, messages: List[Dict]) -> dict:
        """
        使用本地LLM进行关键信息提取
        尝试调用 Ollama API (Qwen2.5-1.5B)
        """
        try:
            import urllib.request

            # 构建对话文本
            conversation = ""
            for msg in messages[-30:]:  # 只取最近30条消息
                role = msg.get("role", "unknown")
                content = msg.get("content", "")[:500]
                conversation += f"[{role}]: {content}\n"

            prompt = f"""你是一个对话分析助手。从以下对话中提取关键信息，以JSON格式返回。

对话内容：
{conversation}

请提取以下四类信息（每个类别最多3条，每条不超过100字）：
1. decisions: 用户明确做出的决定或选择
2. errors: 发现的错误和修正方案
3. insights: 获得的新知识或重要发现
4. preferences: 用户表达的风格偏好或工具偏好

只返回JSON，不要其他内容。格式：{{"decisions": [], "errors": [], "insights": [], "preferences": []}}"""

            data = json.dumps({
                "model": "qwen2.5:1.5b",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 1024}
            }).encode('utf-8')

            req = urllib.request.Request(
                "http://localhost:11434/api/generate",
                data=data,
                headers={"Content-Type": "application/json"}
            )

            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
                response_text = result.get("response", "{}")
                # 尝试解析JSON
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    # 尝试提取JSON部分
                    import re
                    match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if match:
                        return json.loads(match.group())

        except Exception as e:
            print(f"LLM提取失败，回退到规则引擎: {e}")

        # 回退到规则引擎
        return self._rule_extract(messages)

    def _create_memory(self, project_id: str, session_id: str,
                       content: str, memory_type: MemoryType,
                       importance: float = 0.5) -> MemoryFragment:
        """创建记忆碎片"""
        import uuid
        # 自动生成标签
        tags = self._auto_tag(content)

        memory = MemoryFragment(
            memory_id=f"mem_{uuid.uuid4().hex[:12]}",
            project_id=project_id,
            session_id=session_id,
            memory_type=memory_type,
            importance=importance,
            content=content[:500],  # 限制长度
            tags=tags,
            temporal_context={"created_at": time.time(), "session_id": session_id}
        )
        return self.storage.create_memory(memory)

    def _auto_tag(self, content: str) -> List[str]:
        """自动生成标签"""
        tag_map = {
            "ADC0809": ["ADC0809", "模数转换"],
            "8255": ["8255A", "并行接口"],
            "DHT11": ["DHT11", "温湿度传感器"],
            "DS18B20": ["DS18B20", "温度传感器"],
            "DS1302": ["DS1302", "实时时钟"],
            "LCD1602": ["LCD1602", "液晶显示"],
            "数码管": ["数码管", "显示"],
            "LED": ["LED", "指示灯"],
            "串口": ["串口", "UART", "通信"],
            "按键": ["按键", "输入"],
            "Proteus": ["Proteus", "仿真"],
            "Keil": ["Keil", "编译"],
            "代码": ["代码", "编程"],
            "硬件": ["硬件", "电路"],
            "时序": ["时序", "延迟"],
            "中断": ["中断", "ISR"],
            "定时器": ["定时器", "Timer"],
        }
        tags = []
        for keyword, tag_list in tag_map.items():
            if keyword.lower() in content.lower():
                tags.extend(tag_list)
        return list(set(tags))[:5]

    def _update_persona_from_reflection(self, project_id: str,
                                         preferences: List[str]) -> bool:
        """从反思中更新人格"""
        persona = self.storage.get_persona_by_project(project_id)
        if not persona:
            return False

        updated = False
        for pref in preferences:
            pref_lower = pref.lower()
            if any(kw in pref_lower for kw in ["简洁", "简短", "不要太长"]):
                persona.style_preferences["verbosity"] = "concise"
                updated = True
            elif any(kw in pref_lower for kw in ["详细", "详细点", "多说"]):
                persona.style_preferences["verbosity"] = "detailed"
                updated = True
            if any(kw in pref_lower for kw in ["正式", "严谨"]):
                persona.style_preferences["formality"] = "formal"
                updated = True

        if updated:
            persona.version += 1
            persona.updated_at = time.time()
            self.storage.update_persona(persona)

        return updated

    def _generate_summary(self, session: Session, extracted: dict,
                          memory_count: int) -> str:
        """生成反思摘要"""
        parts = []
        parts.append(f"会话 {session.session_id[:20]}... 反思完成")
        parts.append(f"提取记忆: {memory_count} 条")
        parts.append(f"决策: {len(extracted.get('decisions', []))} 条")
        parts.append(f"错误修正: {len(extracted.get('errors', []))} 条")
        parts.append(f"洞察: {len(extracted.get('insights', []))} 条")
        parts.append(f"偏好信号: {len(extracted.get('preferences', []))} 条")
        return " | ".join(parts)

    def incremental_reflect(self, session_id: str,
                            new_messages: List[Dict]) -> dict:
        """
        增量反思 - 长会话中每15轮触发一次
        只提炼新增消息，不重复提炼已有内容
        """
        session = self.storage.get_session(session_id)
        if not session:
            return {"error": f"会话 {session_id} 不存在"}

        # 获取已有记忆数量
        existing_memories = self.storage.get_memories_by_session(session_id)
        existing_count = len(existing_memories)

        # 对新消息做提炼
        result = self.reflect_on_session(session_id, new_messages, use_llm=False)

        # 扣除已有记忆数量
        result["new_memories"] = result["memories_created"] - existing_count
        result["incremental"] = True

        return result

    def should_reflect(self, session_id: str) -> Tuple[bool, str]:
        """
        判断是否应该触发反思

        触发条件（任一满足即触发）：
        1. 会话消息数 >= 15 轮且距上次反思 >= 5 轮
        2. 会话状态变为 completed
        3. 检测到关键事件（错误修复、重大决策）

        Returns:
            (should_reflect, reason)
        """
        session = self.storage.get_session(session_id)
        if not session:
            return (False, "会话不存在")

        if session.status == SessionStatus.COMPLETED:
            return (True, "会话已结束")

        if session.message_count >= 15:
            # 检查距上次反思的轮数
            existing_memories = self.storage.get_memories_by_session(session_id)
            if len(existing_memories) == 0:
                return (True, f"首次反思触发（{session.message_count} 轮）")

            # 简单估算：每条记忆约覆盖5轮对话
            covered_rounds = len(existing_memories) * 5
            if session.message_count - covered_rounds >= 15:
                return (True, f"增量反思触发（{session.message_count} 轮，已覆盖 {covered_rounds} 轮）")

        # 检查关键事件
        recent_events = session.key_events[-5:] if session.key_events else []
        for event in recent_events:
            if event.get("type") in ("error_fix", "major_decision", "bug_resolved"):
                return (True, f"关键事件触发: {event.get('type')}")

        return (False, "未满足触发条件")

    def auto_reflect(self, session_id: str, messages: List[Dict] = None,
                     vector_store=None) -> dict:
        """
        自动反思：检查触发条件 → 执行反思 → 更新人格 → 归档项目

        流程：
        1. 调用 should_reflect(session_id) 检查是否应该反思
        2. 如果应该反思，调用 reflect_on_session(session_id, messages)
        3. 如果 vector_store 可用，将新记忆加入向量存储
        4. 更新项目 context_snapshot
        5. 返回完整的反思结果
        """
        # 1. 检查触发条件
        should_reflect, reason = self.should_reflect(session_id)

        if not should_reflect:
            return {
                "session_id": session_id,
                "reflected": False,
                "reason": reason,
                "result": None
            }

        # 2. 执行反思
        result = self.reflect_on_session(session_id, messages, vector_store=vector_store)

        if "error" in result:
            return {
                "session_id": session_id,
                "reflected": False,
                "reason": result["error"],
                "result": None
            }

        # 3. 将新记忆加入向量存储
        if vector_store is not None:
            try:
                session = self.storage.get_session(session_id)
                if session and session.refined_memories:
                    memories = self.storage.get_memories_by_session(session_id)
                    for mem in memories:
                        try:
                            vector_store.add_memory(mem)
                        except Exception:
                            pass
            except Exception:
                pass

        # 4. 更新项目 context_snapshot
        try:
            session = self.storage.get_session(session_id)
            if session:
                project = self.storage.get_project(session.project_id)
                if project:
                    snapshot_data = {
                        "last_reflection": time.time(),
                        "session_id": session_id,
                        "memories_created": result.get("memories_created", 0),
                        "persona_updated": result.get("persona_updated", False)
                    }
                    project.context_snapshot = json.dumps(snapshot_data, ensure_ascii=False)
                    self.storage.update_project(project)
        except Exception:
            pass

        # 5. 返回完整结果
        return {
            "session_id": session_id,
            "reflected": True,
            "reason": reason,
            "result": result
        }