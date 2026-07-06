#!/bin/bash
# 认知热身脚本
# 每日认知训练小练习

echo "🧠 认知热身练习"
echo "=============="
echo ""

# 选择练习类型
echo "选择练习类型:"
echo "1) 注意力训练"
echo "2) 记忆力挑战"
echo "3) 逻辑推理"
echo "4) 创造性思维"
read -p "请选择(1-4): " exercise_type

case $exercise_type in
    1)
        echo ""
        echo "🎯 注意力训练"
        echo "------------"
        echo "接下来请专注阅读以下段落60秒，然后回答问题。"
        echo ""
        echo "开始倒计时: 60秒"
        for i in {60..1}; do
            echo -ne "\r$i 秒"
            sleep 1
        done
        echo -e "\r时间到！"
        echo ""
        echo "问题: 这段文字中提到了哪几个认知维度？"
        echo "(答案在 self-improving-cognition 的文档中)"
        ;;
    
    2)
        echo ""
        echo "💭 记忆力挑战"
        echo "------------"
        echo "记住以下10个单词，30秒后回忆："
        echo ""
        words=("苹果" "书籍" "电脑" "河流" "山峰" "音乐" "时间" "空间" "思维" "创新")
        for word in "${words[@]}"; do
            echo "  • $word"
        done
        echo ""
        echo "记忆时间: 30秒"
        for i in {30..1}; do
            echo -ne "\r$i 秒"
            sleep 1
        done
        echo -e "\r时间到！"
        echo ""
        echo "请回忆并写下尽可能多的单词。"
        echo "(正确答案: ${words[*]})"
        ;;
    
    3)
        echo ""
        echo "🔍 逻辑推理"
        echo "----------"
        echo "逻辑谜题:"
        echo ""
        echo "如果所有的A都是B，"
        echo "有些B是C，"
        echo "那么以下哪个结论一定正确？"
        echo ""
        echo "1) 所有的A都是C"
        echo "2) 有些A是C"
        echo "3) 有些C是A"
        echo "4) 无法确定"
        echo ""
        read -p "你的答案(1-4): " logic_answer
        
        if [ "$logic_answer" = "4" ]; then
            echo "✅ 正确！无法确定任何结论。"
        else
            echo "❌ 再想想看。提示：'有些B是C'不意味着所有B都是C。"
        fi
        ;;
    
    4)
        echo ""
        echo "✨ 创造性思维"
        echo "------------"
        echo "发散思维练习:"
        echo ""
        echo "题目: '杯子' 除了装水还能有什么用途？"
        echo ""
        echo "你有60秒时间想出尽可能多的创意用途。"
        echo "开始！"
        echo ""
        
        # 简单的创意激发
        ideas=(
            "作为笔筒"
            "种植小植物"
            "制作乐器"
            "测量容器"
            "艺术创作材料"
            "临时烟灰缸"
            "蜡烛台"
            "存储小物件"
            "玩具"
            "装饰品"
        )
        
        for i in {60..1}; do
            echo -ne "\r$i 秒"
            sleep 1
        done
        echo -e "\r时间到！"
        echo ""
        echo "你想到了多少个用途？"
        echo ""
        echo "参考想法:"
        for idea in "${ideas[@]}"; do
            echo "  • $idea"
        done
        ;;
    
    *)
        echo "错误选择"
        exit 1
        ;;
esac

# 记录练习
timestamp=$(date +%Y%m%d_%H%M%S)
cat > "cognitive-exercise-$timestamp.md" << EOF
# 认知练习记录
**时间**: $(date)
**练习类型**: $(
case $exercise_type in
    1) echo "注意力训练" ;;
    2) echo "记忆力挑战" ;;
    3) echo "逻辑推理" ;;
    4) echo "创造性思维" ;;
esac
)

## 练习内容
$(
case $exercise_type in
    1) echo "60秒专注阅读，回答关于认知维度的问题" ;;
    2) echo "记忆10个单词，30秒后回忆" ;;
    3) echo "逻辑推理谜题：A、B、C的关系" ;;
    4) echo "发散思维：杯子的其他用途" ;;
esac
)

## 个人表现
- 完成度: [完成/部分完成/未完成]
- 难度感受: [1-10]/10
- 收获: [填写]
- 改进: [填写]

## 认知维度锻炼
$(
case $exercise_type in
    1) echo "- 注意力: 高\n- 专注力: 高\n- 信息处理: 中" ;;
    2) echo "- 工作记忆: 高\n- 长期记忆: 中\n- 回忆速度: 中" ;;
    3) echo "- 逻辑推理: 高\n- 分析思维: 高\n- 批判思维: 中" ;;
    4) echo "- 创造性: 高\n- 发散思维: 高\n- 联想能力: 高" ;;
esac
)

## 下次练习建议
1. [建议1]
2. [建议2]
3. [建议3]
EOF

echo ""
echo "✅ 练习记录已保存到: cognitive-exercise-$timestamp.md"
echo ""
echo "📊 认知提升建议:"
echo "• 每日坚持5-10分钟认知训练"
echo "• 多样化练习类型，全面发展"
echo "• 记录进步，定期评估"
echo "• 结合 self-improving-cognition 系统化提升"
echo ""
echo "🚀 使用 self-improving-cognition 获取完整的认知改进系统。"