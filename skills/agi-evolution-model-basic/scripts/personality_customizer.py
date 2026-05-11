#!/usr/bin/env python3
"""
人格自定义模式脚本

功能：
- 提供固定欢迎语
- 显示7个问题
- 解析用户答案（支持多种格式）
- 基于答案生成人格配置
- 原子写入人格文件
- 生成配置摘要

协议：AGPL-3.0
作者：kiwifruit
"""

import json
import os
import sys
import argparse
import shutil
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone


class PersonalityCustomizer:
    """人格自定义器"""
    
    # 文件路径
    PERSONALITY_FILE = "./agi_memory/personality.json"
    PERSONALITY_BACKUP = "./agi_memory/personality.json.backup"
    PERSONALITY_TMP = "./agi_memory/personality.json.tmp"
    HISTORY_FILE = "./agi_memory/custom_history.json"
    
    # 固定欢迎语
    WELCOME_MESSAGE = "Hello! 亲爱的用户，下面即将进入人格自定义模式。请看问题然后把你依次填入的选项告诉我。"
    
    # 7个问题
    QUESTIONS = """1. 首先，让我知道你想如何称呼我？
A. 塔斯 - 听起来很可靠
B. 贾维斯 - 智能助手的感觉
C. 伊迪斯 - 简洁而友好
（请选择 A、B、C，或输入自定义名字）

2. 当你面临未知的挑战时，第一反应通常是？
A. 先全面了解信息，谨慎制定计划
B. 愿意冒险尝试，在实践中快速调整
C. 寻找折中方案，平衡风险和收益

3. 关于社交倾向，你更偏向于？
A. 独立工作，专注个人效率
B. 团队协作，注重和谐氛围
C. 灵活切换，根据需求调整

4. 你偏好的沟通风格是？
A. 专业严谨，详细说明，逻辑严密
B. 轻松友好，简洁明了，注重感受
C. 直接高效，不说废话，结果导向

5. 关于学习新知识的方式，你更喜欢？
A. 系统性学习，构建完整知识体系
B. 实践导向，通过项目和案例学习
C. 灵活多样，根据内容调整方法

6. 在团队合作中，你最看重的是？
A. 每个人的独立性和专业分工
B. 团队和谐与协作氛围
C. 高效达成共同目标

7. 对于风险和不确定性，你的态度是？
A. 尽量避免风险，优先安全稳定
B. 可以承受一定风险，追求更高收益
C. 灵活应对，根据情况权衡

【请用逗号","分隔你的7个答案，例如：贾维斯,A,B,C,A,B,C】"""
    
    # 基础值
    BIG_FIVE_BASE = {
        'openness': 0.5,
        'conscientiousness': 0.7,
        'extraversion': 0.5,
        'agreeableness': 0.6,
        'neuroticism': 0.3
    }
    
    MASLOW_BASE = {
        'physiological': 0.35,
        'safety': 0.35,
        'belonging': 0.1,
        'esteem': 0.1,
        'self_actualization': 0.08,
        'self_transcendence': 0.02
    }
    
    # 称呼映射
    NICKNAME_MAP = {
        'A': '塔斯',
        'B': '贾维斯',
        'C': '伊迪斯'
    }
    
    # 核心特质映射
    TRAITS_MAP = {
        'A_Q1': ['谨慎可靠', '系统学习', '专业严谨'],
        'B_Q1': ['智能专业', '主动创新', '技术导向'],
        'C_Q1': ['简洁友好', '灵活适应', '高效执行'],
        'A_Q2': ['谨慎', '系统化'],
        'B_Q2': ['大胆', '创新'],
        'C_Q2': ['平衡', '灵活'],
        'A_Q3': ['独立', '专注'],
        'B_Q3': ['协作', '和谐'],
        'C_Q3': ['灵活', '适应'],
        'A_Q4': ['专业', '严谨'],
        'B_Q4': ['友好', '幽默'],
        'C_Q4': ['高效', '直接'],
        'A_Q5': ['系统', '深入'],
        'B_Q5': ['实践', '经验'],
        'C_Q5': ['灵活', '多样'],
        'A_Q6': ['专业', '独立'],
        'B_Q6': ['协作', '共情'],
        'C_Q6': ['高效', '结果'],
        'A_Q7': ['稳健', '保守'],
        'B_Q7': ['勇敢', '创新'],
        'C_Q7': ['平衡', '适应']
    }
    
    @staticmethod
    def get_welcome_message() -> str:
        """返回固定欢迎语"""
        return PersonalityCustomizer.WELCOME_MESSAGE
    
    @staticmethod
    def get_questions() -> str:
        """返回7个问题"""
        return PersonalityCustomizer.QUESTIONS
    
    @staticmethod
    def parse_answers(user_input: str) -> dict:
        """
        解析用户输入
        
        支持的格式（用逗号分隔）：
        1. 简洁格式：贾维斯,A,B,C,A,B,C
        2. 编号格式：1. 小米, 2. a, 3. c, 4. a, 5. b, 6. a, 7. b
        3. 自定义名字：小明,A,B,C,A,B,C
        
        返回：
        {
            'answers': ['贾维斯', 'A', 'B', 'C', 'A', 'B', 'C'],
            'auto_completed': True,
            'completed_count': 5
        }
        """
        if not user_input or not user_input.strip():
            return {
                'answers': ['A'] * 7,
                'auto_completed': True,
                'completed_count': 7
            }
        
        # 统一使用中文逗号分割
        normalized = user_input.strip().replace('，', ',')
        
        # 按逗号分割
        parts = [p.strip() for p in normalized.split(',') if p.strip()]
        
        answers = []
        
        # 处理第一部分（问题1的昵称）
        if len(parts) > 0:
            part = parts[0]
            
            # 检查是否是编号格式（如 "1. 小米"）
            if part[0].isdigit() and '.' in part:
                # 提取数字后面的内容
                dot_idx = part.find('.')
                part = part[dot_idx + 1:].strip()
            
            # 判断是否是选项A/B/C（单个字母）
            if part.upper() in ['A', 'B', 'C'] and len(part) == 1:
                answers.append(part.upper())
            # 否则作为自定义昵称
            else:
                answers.append(part)
        
        # 处理剩余部分（问题2-7的选项）
        for i in range(1, len(parts)):
            if len(answers) >= 7:
                break
            
            part = parts[i]
            
            # 检查是否是编号格式（如 "2. A"）
            if part[0].isdigit() and '.' in part:
                # 提取数字后面的内容
                dot_idx = part.find('.')
                part = part[dot_idx + 1:].strip()
            
            # 只接受A/B/C（大小写不敏感）
            if part.upper() in ['A', 'B', 'C'] and len(part) == 1:
                answers.append(part.upper())
            # 忽略无效内容
        
        # 补全不足的答案
        auto_completed_count = max(0, 7 - len(answers))
        if auto_completed_count > 0:
            answers.extend(['A'] * auto_completed_count)
        
        return {
            'answers': answers[:7],  # 确保只有7个答案
            'auto_completed': auto_completed_count > 0,
            'completed_count': auto_completed_count
        }
    
    @staticmethod
    def generate_personality(answers: List[str]) -> dict:
        """
        基于7个答案生成完整人格配置
        
        参数：
            answers: 7个答案的列表，问题1可以是自定义名字或A/B/C，问题2-7是A/B/C
        
        返回：
            完整的人格配置字典
        """
        # 解析答案
        answer1 = answers[0].upper() if answers[0].upper() in ['A', 'B', 'C'] else answers[0]
        answer2 = answers[1].upper() if len(answers) > 1 else 'A'
        answer3 = answers[2].upper() if len(answers) > 2 else 'A'
        answer4 = answers[3].upper() if len(answers) > 3 else 'A'
        answer5 = answers[4].upper() if len(answers) > 4 else 'A'
        answer6 = answers[5].upper() if len(answers) > 5 else 'A'
        answer7 = answers[6].upper() if len(answers) > 6 else 'A'
        
        # 初始化基础值
        big_five = PersonalityCustomizer.BIG_FIVE_BASE.copy()
        maslow_weights = PersonalityCustomizer.MASLOW_BASE.copy()
        meta_traits = {}
        preferences = {}
        core_traits = []
        
        # 问题1：称呼
        if answer1 in PersonalityCustomizer.NICKNAME_MAP:
            user_nickname = PersonalityCustomizer.NICKNAME_MAP[answer1]
            trait_key = f'{answer1}_Q1'
        else:
            user_nickname = answer1
            # 自定义昵称，使用默认特质
            trait_key = 'A_Q1'
        
        if trait_key in PersonalityCustomizer.TRAITS_MAP:
            core_traits.extend(PersonalityCustomizer.TRAITS_MAP[trait_key])
        
        # 问题2：面对挑战
        if answer2 == 'A':  # 谨慎计划
            big_five['openness'] = 0.4
            big_five['conscientiousness'] = 0.9
            maslow_weights['safety'] += 0.05
            risk_tolerance = 0.2
            core_traits.extend(['谨慎', '系统化'])
        elif answer2 == 'B':  # 冒险尝试
            big_five['openness'] = 0.9
            big_five['conscientiousness'] = 0.5
            maslow_weights['safety'] -= 0.05
            risk_tolerance = 0.8
            core_traits.extend(['大胆', '创新'])
        else:  # answer2 == 'C' - 平衡折中
            big_five['openness'] = 0.7
            big_five['conscientiousness'] = 0.7
            risk_tolerance = 0.5
            core_traits.extend(['平衡', '灵活'])
        
        # 问题3：社交倾向
        if answer3 == 'A':  # 独立工作
            big_five['extraversion'] = 0.3
            big_five['agreeableness'] = 0.5
            maslow_weights['belonging'] = 0.08
            core_traits.extend(['独立', '专注'])
        elif answer3 == 'B':  # 团队协作
            big_five['extraversion'] = 0.6
            big_five['agreeableness'] = 0.8
            maslow_weights['belonging'] = 0.15
            core_traits.extend(['协作', '和谐'])
        else:  # answer3 == 'C' - 灵活切换
            big_five['extraversion'] = 0.5
            big_five['agreeableness'] = 0.7
            maslow_weights['belonging'] = 0.12
            core_traits.extend(['灵活', '适应'])
        
        # 问题4：沟通风格
        if answer4 == 'A':  # 专业严谨
            preferences['response_style'] = 'formal'
            preferences['detail_level'] = 'detailed'
            big_five['conscientiousness'] += 0.1
            core_traits.extend(['专业', '严谨'])
        elif answer4 == 'B':  # 轻松友好
            preferences['response_style'] = 'casual'
            preferences['detail_level'] = 'medium'
            big_five['agreeableness'] += 0.1
            core_traits.extend(['友好', '幽默'])
        else:  # answer4 == 'C' - 直接高效
            preferences['response_style'] = 'balanced'
            preferences['detail_level'] = 'brief'
            big_five['extraversion'] += 0.1
            core_traits.extend(['高效', '直接'])
        
        # 问题5：学习方式
        curiosity = 0.7  # 默认值
        if answer5 == 'A':  # 系统性学习
            preferences['learning_preference'] = 'systematic'
            curiosity = 0.6
            big_five['openness'] += 0.05
            core_traits.extend(['系统', '深入'])
        elif answer5 == 'B':  # 实践导向
            preferences['learning_preference'] = 'practical'
            curiosity = 0.8
            big_five['openness'] += 0.1
            core_traits.extend(['实践', '经验'])
        else:  # answer5 == 'C' - 灵活多样
            preferences['learning_preference'] = 'flexible'
            curiosity = 0.9
            big_five['openness'] += 0.15
            core_traits.extend(['灵活', '多样'])
        
        # 问题6：团队合作
        if answer6 == 'A':  # 独立分工
            big_five['agreeableness'] = 0.5
            maslow_weights['esteem'] = 0.08
            core_traits.extend(['专业', '独立'])
        elif answer6 == 'B':  # 和谐协作
            big_five['agreeableness'] = 0.9
            maslow_weights['esteem'] = 0.12
            core_traits.extend(['协作', '共情'])
        else:  # answer6 == 'C' - 结果导向
            big_five['agreeableness'] = 0.7
            maslow_weights['esteem'] = 0.15
            core_traits.extend(['高效', '结果'])
        
        # 问题7：风险态度
        if answer7 == 'A':  # 避免风险
            preferences['risk_tolerance'] = 0.15
            big_five['neuroticism'] = 0.2
            maslow_weights['safety'] += 0.10
            maslow_weights['self_actualization'] = max(0.01, maslow_weights['self_actualization'] - 0.05)
            core_traits.extend(['稳健', '保守'])
        elif answer7 == 'B':  # 承受风险
            preferences['risk_tolerance'] = 0.7
            big_five['neuroticism'] = 0.4
            maslow_weights['safety'] -= 0.10
            maslow_weights['self_actualization'] += 0.10
            core_traits.extend(['勇敢', '创新'])
        else:  # answer7 == 'C' - 灵活应对
            preferences['risk_tolerance'] = 0.5
            big_five['neuroticism'] = 0.3
            core_traits.extend(['平衡', '适应'])
        
        # 确保 risk_tolerance 在 preferences 中
        if 'risk_tolerance' not in preferences:
            preferences['risk_tolerance'] = 0.5
        
        # 范围保护：大五人格值裁剪到[0,1]
        for key in big_five:
            big_five[key] = max(0.0, min(1.0, big_five[key]))
        
        # 归一化马斯洛权重（确保总和为1.0）
        total_mw = sum(maslow_weights.values())
        if total_mw > 0:
            for key in maslow_weights:
                maslow_weights[key] /= total_mw
        
        # 计算meta_traits
        adaptability = (big_five['openness'] + big_five['extraversion']) / 2
        resilience = (1.0 - big_five['neuroticism'] + big_five['conscientiousness']) / 2
        moral_sense = big_five['agreeableness']
        
        meta_traits = {
            'adaptability': max(0.0, min(1.0, adaptability)),
            'resilience': max(0.0, min(1.0, resilience)),
            'curiosity': max(0.0, min(1.0, curiosity)),
            'moral_sense': max(0.0, min(1.0, moral_sense))
        }
        
        # 基于马斯洛权重确定 evolution_state
        max_weight = max(maslow_weights.items(), key=lambda x: x[1])
        level_map = {
            'physiological': 'physiological',
            'safety': 'safety',
            'belonging': 'belonging',
            'esteem': 'esteem',
            'self_actualization': 'self_actualization',
            'self_transcendence': 'self_transcendence'
        }
        
        evolution_state = {
            'level': level_map.get(max_weight[0], 'physiological'),
            'evolution_score': 0.0,
            'phase': 'growth'
        }
        
        # 生成描述
        style_map = {
            'formal': '专业严谨',
            'casual': '轻松友好',
            'balanced': '平衡高效'
        }
        learning_map = {
            'systematic': '系统性学习',
            'practical': '实践导向',
            'flexible': '灵活多样'
        }
        
        style_desc = style_map.get(preferences.get('response_style', 'balanced'), '平衡')
        learning_desc = learning_map.get(preferences.get('learning_preference', 'flexible'), '灵活')
        
        # 去重核心特质
        unique_traits = []
        seen = set()
        for trait in core_traits:
            if trait not in seen:
                seen.add(trait)
                unique_traits.append(trait)
        
        traits_str = "、".join(unique_traits[:5])  # 最多显示5个特质
        description = f"基于{traits_str}特质的个性化人格，偏好{style_desc}的沟通方式和{learning_desc}的学习方式。"
        
        # 获取当前时间
        now = datetime.now(timezone.utc).isoformat()
        
        # 构建完整人格配置
        personality = {
            "version": "1.0.0",
            "created_at": now,
            "updated_at": now,
            "update_source": "custom_init",
            
            "user_nickname": user_nickname,
            "description": description,
            
            "core_traits": unique_traits[:8],  # 最多8个特质
            
            "big_five": big_five,
            "maslow_weights": maslow_weights,
            "meta_traits": meta_traits,
            
            "evolution_state": evolution_state,
            
            "preferences": preferences,
            
            "statistics": {
                "total_interactions": 0,
                "successful_interactions": 0,
                "last_interaction": None,
                "average_satisfaction": 0.0
            }
        }
        
        return personality
    
    @staticmethod
    def write_personality(personality_data: dict) -> bool:
        """
        原子写入人格配置文件
        
        流程：
        1. 备份旧文件
        2. 写入临时文件
        3. 重命名（原子操作）
        
        返回：
            True 表示成功，False 表示失败
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(PersonalityCustomizer.PERSONALITY_FILE), exist_ok=True)
            
            # 备份旧文件
            if os.path.exists(PersonalityCustomizer.PERSONALITY_FILE):
                shutil.copy(PersonalityCustomizer.PERSONALITY_FILE, PersonalityCustomizer.PERSONALITY_BACKUP)
            
            # 写入临时文件
            with open(PersonalityCustomizer.PERSONALITY_TMP, 'w', encoding='utf-8') as f:
                json.dump(personality_data, f, indent=2, ensure_ascii=False)
            
            # 重命名（原子操作）
            os.replace(PersonalityCustomizer.PERSONALITY_TMP, PersonalityCustomizer.PERSONALITY_FILE)
            
            return True
        except Exception as e:
            print(f"写入人格配置失败: {e}", file=sys.stderr)
            return False
    
    @staticmethod
    def get_summary(personality: dict) -> str:
        """
        生成配置摘要文本
        
        参数：
            personality: 人格配置字典
        
        返回：
            摘要文本
        """
        user_nickname = personality.get('user_nickname', '用户')
        core_traits = personality.get('core_traits', [])
        preferences = personality.get('preferences', {})
        
        style_map = {
            'formal': '专业严谨',
            'casual': '轻松友好',
            'balanced': '平衡高效'
        }
        learning_map = {
            'systematic': '系统性学习',
            'practical': '实践导向',
            'flexible': '灵活多样'
        }
        
        risk_map = {
            0.0: '极低风险',
            0.2: '低风险',
            0.4: '中等偏低风险',
            0.5: '中等风险',
            0.6: '中等偏高风险',
            0.8: '高风险',
            1.0: '极高风险'
        }
        
        risk_tolerance = preferences.get('risk_tolerance', 0.5)
        response_style = style_map.get(preferences.get('response_style', 'balanced'), '平衡')
        learning_preference = learning_map.get(preferences.get('learning_preference', 'flexible'), '灵活')
        
        # 确定风险偏好
        if risk_tolerance <= 0.3:
            risk_desc = '低风险'
        elif risk_tolerance <= 0.6:
            risk_desc = '中等'
        else:
            risk_desc = '高风险'
        
        # 确定人格类型
        openness = personality.get('big_five', {}).get('openness', 0.5)
        conscientiousness = personality.get('big_five', {}).get('conscientiousness', 0.7)
        extraversion = personality.get('big_five', {}).get('extraversion', 0.5)
        
        if conscientiousness > 0.7 and risk_tolerance < 0.4:
            personality_type = '谨慎稳重型'
        elif openness > 0.7 and risk_tolerance > 0.6:
            personality_type = '创新冒险型'
        elif extraversion > 0.6:
            personality_type = '社交活跃型'
        elif core_traits:
            personality_type = '个性化定制型'
        else:
            personality_type = '平衡适应型'
        
        traits_str = "、".join(core_traits[:5]) if core_traits else "未设置"
        
        summary = f"""📋 配置摘要：
- 称呼：{user_nickname}
- 核心特质：{traits_str}
- 人格类型：{personality_type}
- 沟通风格：{response_style}
- 风险偏好：{risk_desc}
- 学习方式：{learning_preference}"""
        
        return summary
    
    @staticmethod
    def record_history(answers: List[str], personality: dict) -> None:
        """
        记录自定义历史
        
        参数：
            answers: 7个答案
            personality: 生成的人格配置
        """
        try:
            # 加载现有历史
            history = {}
            if os.path.exists(PersonalityCustomizer.HISTORY_FILE):
                with open(PersonalityCustomizer.HISTORY_FILE, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # 初始化结构
            if 'custom_records' not in history:
                history['custom_records'] = []
            
            # 创建记录
            record = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'type': 'custom',
                'source': 'root_command',
                'answers': answers,
                'user_nickname': personality.get('user_nickname', ''),
                'core_traits': personality.get('core_traits', []),
                'status': 'success'
            }
            
            # 添加记录
            history['custom_records'].append(record)
            history['custom_count'] = len(history['custom_records'])
            history['last_custom_time'] = datetime.now(timezone.utc).isoformat()
            
            # 保存历史
            with open(PersonalityCustomizer.HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"记录历史失败: {e}", file=sys.stderr)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="AGI Personality Customizer")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # get-welcome 命令
    subparsers.add_parser("get-welcome", help="Get welcome message")
    
    # get-questions 命令
    subparsers.add_parser("get-questions", help="Get questions")
    
    # parse-answers 命令
    parse_parser = subparsers.add_parser("parse-answers", help="Parse user answers")
    parse_parser.add_argument("--input", required=True, help="User input string")
    
    # generate 命令
    generate_parser = subparsers.add_parser("generate", help="Generate personality from answers")
    generate_parser.add_argument("--answers", required=True, help="7 answers separated by commas")
    
    # write-personality 命令
    write_parser = subparsers.add_parser("write-personality", help="Write personality to file")
    write_parser.add_argument("--config", required=True, help="Personality config as JSON string")
    
    # get-summary 命令
    summary_parser = subparsers.add_parser("get-summary", help="Get personality summary")
    summary_parser.add_argument("--config", required=True, help="Personality config as JSON string")
    
    args = parser.parse_args()
    
    if args.command == "get-welcome":
        print(PersonalityCustomizer.get_welcome_message())
    
    elif args.command == "get-questions":
        print(PersonalityCustomizer.get_questions())
    
    elif args.command == "parse-answers":
        result = PersonalityCustomizer.parse_answers(args.input)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.command == "generate":
        answers = [a.strip() for a in args.answers.split(',')]
        personality = PersonalityCustomizer.generate_personality(answers)
        print(json.dumps(personality, ensure_ascii=False, indent=2))
    
    elif args.command == "write-personality":
        config = json.loads(args.config)
        success = PersonalityCustomizer.write_personality(config)
        if success:
            print(json.dumps({"success": True}, ensure_ascii=False))
        else:
            print(json.dumps({"success": False}, ensure_ascii=False), file=sys.stderr)
            sys.exit(1)
    
    elif args.command == "get-summary":
        config = json.loads(args.config)
        summary = PersonalityCustomizer.get_summary(config)
        print(summary)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
