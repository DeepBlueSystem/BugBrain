from core.brain import BugBrain

# 创建一个大脑
brain = BugBrain()

# 构造5个感知输入
sensory_input = [0.1, -0.2, 0.5, 0.8, 0.3]

# 大脑思考
output = brain(sensory_input)
print("移动方向 dx, dy：", output)

# 复制大脑（遗传）
brain2 = brain.copy()

# 突变
brain2.mutate()

print("✅ PyTorch 大脑测试成功！")