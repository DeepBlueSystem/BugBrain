import torch
import torch.nn as nn
import random

# 虫子的大脑神经网络类（用于遗传算法 / AI 进化）
class BugBrain(nn.Module):
    # 初始化神经网络
    # input_size: 输入维度（虫子感知到的信息）
    # hidden_size: 隐藏层神经元数量
    # output_size: 输出维度（虫子的动作决策）
    def __init__(self, input_size=5, hidden_size=8, output_size=2):
        super().__init__()  # 调用父类初始化
        self.fc1 = nn.Linear(input_size, hidden_size)  # 第一层全连接
        self.fc2 = nn.Linear(hidden_size, output_size) # 第二层全连接
        self.act = nn.Tanh()  # 激活函数，把输出限制在 -1~1 之间

    # 前向传播（推理：输入 → 输出）
    def forward(self, x):
        # 如果输入不是张量，自动转换成 PyTorch 张量
        if not isinstance(x, torch.Tensor):
            x = torch.tensor(x, dtype=torch.float32)
        
        # 第一层 + 激活
        x = self.act(self.fc1(x))
        # 第二层 + 激活
        x = self.act(self.fc2(x))
        return x  # 返回最终决策

    # 复制一个一模一样的大脑（用于遗传繁殖）
    def copy(self):
        # 创建新的大脑实例
        new_brain = BugBrain(
            input_size=self.fc1.in_features,
            hidden_size=self.fc1.out_features,
            output_size=self.fc2.out_features
        )
        # 把当前大脑的权重复制给新大脑
        new_brain.load_state_dict(self.state_dict())
        return new_brain

    # 变异：随机改变一些权重（遗传算法核心）
    # mutation_rate: 每个参数有多少概率被修改
    # strength: 变异强度
    def mutate(self, mutation_rate=0.1, strength=0.1):
        with torch.no_grad():  # 不计算梯度（纯修改权重）
            # 遍历神经网络所有参数
            for param in self.parameters():
                # 按概率随机变异
                if random.random() < mutation_rate:
                    # 加上随机噪声
                    param.add_(torch.randn_like(param) * strength)

    # ========== 保存 / 加载大脑模型 ==========
    # 保存神经网络权重到文件
    def save(self, path):
        torch.save(self.state_dict(), path)

    # 从文件加载神经网络权重
    def load(self, path):
        self.load_state_dict(torch.load(path))