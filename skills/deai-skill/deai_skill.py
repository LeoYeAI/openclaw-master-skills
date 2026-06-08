import json
import re
import random
import argparse
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import sys

try:
    import jieba
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    print("Warning: jieba not installed. Some features may not work optimally.")


class AITextDetector:
    """AI文本特征检测器"""
    
    def __init__(self, config_path: str = "rules.json"):
        """初始化检测器，加载配置"""
        self.config = self._load_config(config_path)
        self.chinese_features = self.config.get("chinese_ai_features", {})
        self.english_features = self.config.get("english_ai_features", {})
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file {config_path} not found. Using default config.")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "chinese_ai_features": {
                "transition_words": ["综上所述", "值得注意的是", "需要强调的是", "此外", "另外"],
                "formal_words": ["具有", "表现出", "体现", "实现", "呈现"],
                "idioms": ["举足轻重", "息息相关", "必不可少", "至关重要", "不可或缺"]
            },
            "english_ai_features": {
                "transition_words": ["furthermore", "moreover", "in addition", "additionally"],
                "formal_words": ["possess", "exhibit", "demonstrate", "implement", "display"],
                "idioms": ["play a crucial role", "of great importance", "significant impact"]
            }
        }
    
    def detect_ai_features(self, text: str, language: str = 'zh') -> Dict:
        """
        检测文本中的AI特征
        
        Args:
            text: 待检测文本
            language: 语言类型 ('zh' 或 'en')
            
        Returns:
            包含AI特征信息的字典
        """
        features = {
            'ai_score': 0.0,
            'ai_phrases': [],
            'sentence_similarity': 0.0,
            'formal_word_count': 0
        }
        
        if language == 'zh':
            self._detect_chinese_features(text, features)
        else:
            self._detect_english_features(text, features)
        
        # 计算综合AI分数
        features['ai_score'] = self._calculate_ai_score(features)
        
        return features
    
    def _detect_chinese_features(self, text: str, features: Dict):
        """检测中文AI特征"""
        # 检测过渡词
        transition_matches = []
        for word in self.chinese_features.get("transition_words", []):
            matches = re.finditer(word, text)
            transition_matches.extend([m.group() for m in matches])
        features['ai_phrases'].extend(transition_matches)
        
        # 检测正式词汇
        formal_matches = []
        for word in self.chinese_features.get("formal_words", []):
            matches = re.finditer(word, text)
            formal_matches.extend([m.group() for m in matches])
        features['formal_word_count'] = len(formal_matches)
        
        # 检测成语
        idiom_matches = []
        for idiom in self.chinese_features.get("idioms", []):
            if idiom in text:
                idiom_matches.append(idiom)
        features['ai_phrases'].extend(idiom_matches)
        
        # 检测句式特征（使用jieba分词）
        if JIEBA_AVAILABLE:
            sentences = re.split('[。！？]', text)
            sentence_lengths = [len(s) for s in sentences if s.strip()]
            if len(sentence_lengths) > 1:
                avg_length = sum(sentence_lengths) / len(sentence_lengths)
                std_dev = (sum((x - avg_length) ** 2 for x in sentence_lengths) / len(sentence_lengths)) ** 0.5
                features['sentence_similarity'] = max(0, 1 - std_dev / avg_length)
    
    def _detect_english_features(self, text: str, features: Dict):
        """检测英文AI特征"""
        text_lower = text.lower()
        
        # 检测过渡词
        transition_matches = []
        for word in self.english_features.get("transition_words", []):
            pattern = r'\b' + word + r'\b'
            matches = re.findall(pattern, text_lower)
            transition_matches.extend(matches)
        features['ai_phrases'].extend(transition_matches)
        
        # 检测正式词汇
        formal_matches = []
        for word in self.english_features.get("formal_words", []):
            pattern = r'\b' + word + r'\b'
            matches = re.findall(pattern, text_lower)
            formal_matches.extend(matches)
        features['formal_word_count'] = len(formal_matches)
        
        # 检测常用AI短语
        common_phrases = self.english_features.get("idioms", [])
        for phrase in common_phrases:
            if phrase.lower() in text_lower:
                features['ai_phrases'].append(phrase)
        
        # 检测句式特征
        sentences = re.split(r'[.!?]+', text)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        if len(sentence_lengths) > 1:
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            std_dev = (sum((x - avg_length) ** 2 for x in sentence_lengths) / len(sentence_lengths)) ** 0.5
            features['sentence_similarity'] = max(0, 1 - std_dev / avg_length)
    
    def _calculate_ai_score(self, features: Dict) -> float:
        """计算AI特征综合分数"""
        # 基础分数
        score = 0.0
        
        # AI短语权重
        phrase_count = len(features['ai_phrases'])
        score += min(phrase_count * 0.15, 0.5)
        
        # 正式词汇权重
        formal_count = features['formal_word_count']
        score += min(formal_count * 0.1, 0.3)
        
        # 句式相似度权重
        score += features['sentence_similarity'] * 0.2
        
        return min(score, 1.0)


class TextHumanizer:
    """文本人性化处理器"""
    
    def __init__(self, config_path: str = "rules.json"):
        """初始化人性化处理器"""
        self.config = self._load_config(config_path)
        self.conversion_rules = self.config.get("conversion_rules", {})
        self.colloquial = self.config.get("colloquial_expressions", {})
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file {config_path} not found. Using default config.")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "conversion_rules": {
                "zh": {
                    "transition_replacements": {
                        "综上所述": ["总的来说", "简而言之", "总的来说吧", "这么看的话"],
                        "值得注意的是": ["要知道", "得注意一下", "值得注意的是", "有一点要提醒"],
                        "需要强调的是": ["重点是", "关键在于", "得强调下", "主要是"],
                        "此外": ["还有", "另外", "而且", "再说了"],
                        "另外": ["还有", "对了", "再加上"]
                    },
                    "formal_word_replacements": {
                        "具有": ["有", "拥有", "具备"],
                        "表现出": ["显示出", "表现出", "展示出"],
                        "体现": ["表现出", "显示出", "体现了"],
                        "实现": ["做到", "达成", "完成"],
                        "呈现": ["展现出", "表现出", "显现出"]
                    },
                    "sentence_patterns": [
                        (r"我们可以(看出|看出)(.+)", r"从\2来看"),
                        (r"应该(注意|认识到)(.+)", r"要注意\2"),
                        (r"(.+)(具有|表现出)(.+)的特点", r"\1看起来\3"),
                        (r"(.+)(对于|关于)(.+)具有重要意义", r"\1\3很重要"),
                    ]
                },
                "en": {
                    "transition_replacements": {
                        "furthermore": ["also", "plus", "on top of that"],
                        "moreover": ["also", "besides", "what's more"],
                        "in addition": ["also", "plus", "another thing"],
                        "additionally": ["also", "plus", "another point"]
                    },
                    "formal_word_replacements": {
                        "possess": ["have", "own", "got"],
                        "exhibit": ["show", "display", "demonstrate"],
                        "demonstrate": ["show", "display", "prove"],
                        "implement": ["put in place", "set up", "start"],
                        "display": ["show", "display", "reveal"]
                    },
                    "sentence_patterns": [
                        (r"we can (see|observe) that", r"it's clear that"),
                        (r"it is important to (note|recognize)", r"we should keep in mind"),
                        (r"(.+)(demonstrates|exhibits)(.+) characteristics", r"\1seems\3"),
                        (r"(.+)(is of great|has significant) importance", r"\1is really important"),
                    ]
                }
            },
            "colloquial_expressions": {
                "zh": {
                    "endings": ["吧", "呢", "啊", "呀", "的", "啦", "嘛"],
                    "fillers": ["你知道", "那个", "其实", "说真的", "反正"],
                    "uncertainties": ["好像", "大概", "可能", "也许", "差不多"]
                },
                "en": {
                    "endings": [", right?", ", isn't it?", ", you know?", ", you see?"],
                    "fillers": ["you know", "I mean", "like", "actually", "basically"],
                    "uncertainties": ["sort of", "kind of", "maybe", "probably", "I guess"]
                }
            }
        }
    
    def humanize_text(self, text: str, language: str = 'zh', style: str = 'natural') -> str:
        """
        人性化处理文本
        
        Args:
            text: 待处理文本
            language: 语言类型 ('zh' 或 'en')
            style: 处理风格 ('natural', 'casual', 'formal')
            
        Returns:
            处理后的文本
        """
        if style == 'formal':
            # 正式风格：仅做轻微调整
            return self._apply_formal_style(text, language)
        elif style == 'casual':
            # 口语风格：大幅度口语化
            return self._apply_casual_style(text, language)
        else:
            # 自然风格：平衡处理
            return self._apply_natural_style(text, language)
    
    def _apply_natural_style(self, text: str, language: str) -> str:
        """应用自然风格处理"""
        # 应用过渡词替换
        text = self._replace_transitions(text, language, probability=0.7)
        
        # 应用正式词汇替换
        text = self._replace_formal_words(text, language, probability=0.6)
        
        # 应用句式模式转换
        text = self._apply_sentence_patterns(text, language, probability=0.5)
        
        # 添加轻微的口语化元素
        text = self._add_colloquial_elements(text, language, intensity='mild')
        
        return text
    
    def _apply_casual_style(self, text: str, language: str) -> str:
        """应用口语风格处理"""
        # 更积极地替换过渡词
        text = self._replace_transitions(text, language, probability=0.9)
        
        # 更积极地替换正式词汇
        text = self._replace_formal_words(text, language, probability=0.8)
        
        # 更多应用句式模式转换
        text = self._apply_sentence_patterns(text, language, probability=0.7)
        
        # 添加更多口语化元素
        text = self._add_colloquial_elements(text, language, intensity='strong')
        
        return text
    
    def _apply_formal_style(self, text: str, language: str) -> str:
        """应用正式风格处理（保持专业性）"""
        # 仅替换最明显的AI特征
        text = self._replace_transitions(text, language, probability=0.4)
        
        # 少量替换正式词汇
        text = self._replace_formal_words(text, language, probability=0.3)
        
        # 轻微应用句式模式转换
        text = self._apply_sentence_patterns(text, language, probability=0.2)
        
        return text
    
    def _replace_transitions(self, text: str, language: str, probability: float) -> str:
        """替换过渡词"""
        rules = self.conversion_rules.get(language, {}).get("transition_replacements", {})
        
        for original, replacements in rules.items():
            pattern = re.escape(original)
            def replace_func(match):
                if random.random() < probability:
                    return random.choice(replacements)
                return match.group()
            text = re.sub(pattern, replace_func, text, flags=re.IGNORECASE if language == 'en' else 0)
        
        return text
    
    def _replace_formal_words(self, text: str, language: str, probability: float) -> str:
        """替换正式词汇"""
        rules = self.conversion_rules.get(language, {}).get("formal_word_replacements", {})
        
        for original, replacements in rules.items():
            pattern = r'\b' + re.escape(original) + r'\b'
            def replace_func(match):
                if random.random() < probability:
                    return random.choice(replacements)
                return match.group()
            text = re.sub(pattern, replace_func, text, flags=re.IGNORECASE if language == 'en' else 0)
        
        return text
    
    def _apply_sentence_patterns(self, text: str, language: str, probability: float) -> str:
        """应用句式模式转换 - 使用简单的字符串替换"""
        # 定义内置的替换规则
        built_in_rules = {
            'zh': [
                (r"具有(.+)的作用和意义", lambda m: f"{m.group(1)}很重要"),
                (r"具有(.+)的意义", lambda m: f"{m.group(1)}挺重要"),
                (r"具有(.+)的特点", lambda m: f"{m.group(1)}"),
                (r"我们可以(.+)看出", lambda m: f"从{m.group(1)}看"),
                (r"需要(.+)的是", lambda m: f"要注意{m.group(1)}"),
                (r"(.+)具有重要意义", lambda m: f"{m.group(1)}很重要"),
            ],
            'en': [
                (r"it is important to note that", "we should keep in mind that"),
                (r"it should be noted that", "remember that"),
                (r"it is worth noting that", "it's worth saying that"),
                (r"we can see that", "it's clear that"),
                (r"we can observe that", "it's clear that"),
                (r"in order to", "to"),
                (r"with regard to", "about"),
            ]
        }
        
        rules = built_in_rules.get(language, [])
        
        for rule in rules:
            if isinstance(rule, tuple) and len(rule) == 2:
                pattern, replacement = rule
                
                def replace_func(match):
                    if random.random() < probability:
                        if callable(replacement):
                            return replacement(match)
                        return replacement
                    return match.group()
                
                flags = re.IGNORECASE if language == 'en' else 0
                text = re.sub(pattern, replace_func, text, flags=flags)
        
        return text
    
    def _add_colloquial_elements(self, text: str, language: str, intensity: str = 'mild') -> str:
        """添加口语化元素"""
        colloquial_dict = self.colloquial.get(language, {})
        
        # 根据强度调整添加概率
        if intensity == 'mild':
            filler_prob = 0.15
            ending_prob = 0.2
            uncertainty_prob = 0.1
        elif intensity == 'strong':
            filler_prob = 0.3
            ending_prob = 0.4
            uncertainty_prob = 0.2
        else:
            return text
        
        # 分割句子
        if language == 'zh':
            sentences = re.split('([。！？])', text)
        else:
            sentences = re.split('([.!?]+)', text)
        
        processed_sentences = []
        for i in range(0, len(sentences), 2):
            if i >= len(sentences):
                break
                
            sentence = sentences[i]
            punctuation = sentences[i+1] if i+1 < len(sentences) else ''
            
            if not sentence.strip():
                processed_sentences.append(sentence + punctuation)
                continue
            
            # 添加语气词/填充词
            fillers = colloquial_dict.get("fillers", [])
            if fillers and random.random() < filler_prob and i > 0:
                sentence = random.choice(fillers) + "，" + sentence
            
            # 添加不确定性表达
            uncertainties = colloquial_dict.get("uncertainties", [])
            if uncertainties and random.random() < uncertainty_prob:
                uncertainty = random.choice(uncertainties)
                if language == 'zh':
                    # 在中文句子中适当位置插入
                    words = list(sentence)
                    insert_pos = random.randint(1, len(words)//2)
                    sentence = ''.join(words[:insert_pos]) + uncertainty + ''.join(words[insert_pos:])
                else:
                    # 在英文句子前插入
                    sentence = uncertainty + " " + sentence
            
            # 添加句尾语气词
            endings = colloquial_dict.get("endings", [])
            if endings and punctuation and random.random() < ending_prob:
                ending = random.choice(endings)
                if language == 'zh':
                    punctuation = ending + punctuation
                else:
                    punctuation = ending + punctuation
            
            processed_sentences.append(sentence + punctuation)
        
        return ''.join(processed_sentences)


class DeAIProcessor:
    """AI文本去味处理器 - 主类"""
    
    def __init__(self, config_path: str = "rules.json"):
        """初始化处理器"""
        self.detector = AITextDetector(config_path)
        self.humanizer = TextHumanizer(config_path)
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file {config_path} not found. Using default config.")
            return {}
    
    def process(self, text: str, language: str = 'zh', style: str = 'natural', 
                detect_only: bool = False) -> Tuple[str, Optional[Dict]]:
        """
        处理文本，去除AI特征
        
        Args:
            text: 待处理文本
            language: 语言类型 ('zh' 或 'en')
            style: 处理风格 ('natural', 'casual', 'formal')
            detect_only: 是否只检测不处理
            
        Returns:
            (处理后的文本, AI特征信息) 或 (原文, AI特征信息) 如果detect_only为True
        """
        # 检测AI特征
        features = self.detector.detect_ai_features(text, language)
        
        if detect_only:
            return text, features
        
        # 人性化处理
        humanized_text = self.humanizer.humanize_text(text, language, style)
        
        return humanized_text, features
    
    def batch_process(self, texts: List[str], language: str = 'zh', 
                     style: str = 'natural') -> List[Tuple[str, Dict]]:
        """
        批量处理文本
        
        Args:
            texts: 文本列表
            language: 语言类型
            style: 处理风格
            
        Returns:
            处理结果列表，每个元素为(处理后的文本, AI特征信息)
        """
        results = []
        for text in texts:
            humanized_text, features = self.process(text, language, style)
            results.append((humanized_text, features))
        return results
    
    def get_ai_score(self, text: str, language: str = 'zh') -> float:
        """
        获取文本的AI特征分数
        
        Args:
            text: 待检测文本
            language: 语言类型
            
        Returns:
            AI特征分数 (0-1)
        """
        features = self.detector.detect_ai_features(text, language)
        return features['ai_score']


def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(description='AI文本去味工具 - 去除AI生成文本的AI特征')
    parser.add_argument('--input', '-i', type=str, help='输入文件路径')
    parser.add_argument('--output', '-o', type=str, help='输出文件路径')
    parser.add_argument('--input_dir', type=str, help='输入目录路径（批量处理）')
    parser.add_argument('--output_dir', type=str, help='输出目录路径（批量处理）')
    parser.add_argument('--language', '-l', type=str, default='zh', choices=['zh', 'en'],
                       help='文本语言 (zh:中文, en:英文)')
    parser.add_argument('--style', '-s', type=str, default='natural',
                       choices=['natural', 'casual', 'formal'],
                       help='处理风格 (natural:自然, casual:口语, formal:正式)')
    parser.add_argument('--detect', '-d', action='store_true',
                       help='仅检测AI特征，不进行处理')
    parser.add_argument('--text', '-t', type=str, help='直接处理输入的文本')
    
    args = parser.parse_args()
    
    # 创建处理器
    processor = DeAIProcessor()
    
    # 处理直接输入的文本
    if args.text:
        result, features = processor.process(args.text, args.language, args.style, args.detect)
        print(f"原文: {args.text}")
        print(f"AI特征分数: {features['ai_score']:.2f}")
        print(f"检测到的AI特征: {features['ai_phrases']}")
        if not args.detect:
            print(f"处理后: {result}")
        return
    
    # 批量处理目录
    if args.input_dir and args.output_dir:
        input_path = Path(args.input_dir)
        output_path = Path(args.output_dir)
        
        if not input_path.exists():
            print(f"错误: 输入目录 {args.input_dir} 不存在")
            return
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        for file in input_path.glob('*'):
            if file.is_file() and file.suffix in ['.txt', '.md']:
                with open(file, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                result, features = processor.process(text, args.language, args.style, args.detect)
                
                output_file = output_path / file.name
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result)
                
                print(f"处理完成: {file.name}")
                print(f"AI特征分数: {features['ai_score']:.2f}")
        return
    
    # 处理单个文件
    if args.input and args.output:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                text = f.read()
            
            result, features = processor.process(text, args.language, args.style, args.detect)
            
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            
            print(f"处理完成: {args.input} -> {args.output}")
            print(f"AI特征分数: {features['ai_score']:.2f}")
            if features['ai_phrases']:
                print(f"检测到的AI特征: {', '.join(features['ai_phrases'][:10])}")
        
        except FileNotFoundError:
            print(f"错误: 输入文件 {args.input} 不存在")
        except Exception as e:
            print(f"处理文件时出错: {str(e)}")
        return
    
    # 交互模式
    print("AI文本去味工具 - 交互模式")
    print("输入'quit'或'exit'退出\n")
    
    while True:
        try:
            text = input("请输入要处理的文本: ")
            if text.lower() in ['quit', 'exit']:
                break
            
            if not text.strip():
                continue
            
            result, features = processor.process(text, args.language, args.style, args.detect)
            
            print(f"\nAI特征分数: {features['ai_score']:.2f}")
            if features['ai_phrases']:
                print(f"检测到的AI特征: {', '.join(features['ai_phrases'][:10])}")
            if not args.detect:
                print(f"\n处理结果:\n{result}\n")
            else:
                print()
        
        except KeyboardInterrupt:
            print("\n退出程序")
            break
        except Exception as e:
            print(f"处理出错: {str(e)}")


if __name__ == '__main__':
    main()