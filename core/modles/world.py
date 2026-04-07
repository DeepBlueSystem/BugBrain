import random
import os
# 创建保存大脑模型的文件夹（如果不存在）
os.makedirs("bugs", exist_ok=True)
os.makedirs("predators", exist_ok=True)

# 食物类：虫子吃的能量补给
class Food:
    def __init__(self, config):
        # 随机生成在世界范围内的位置
        self.x = random.randint(0, config['world']['width'])
        self.y = random.randint(0, config['world']['height'])
        self.color = (0, 255, 80)  # 绿色食物

# 世界类：整个生态系统的管理者（虫子、捕食者、食物）
class World:
    def __init__(self, config, Bug, Predator):
        self.config = config          # 全局配置（宽、高、速度等）
        self.Bug = Bug                # 虫子类引用
        self.Predator = Predator    # 捕食者类引用

        # 初始化种群
        self.bugs = [Bug(config=config) for _ in range(30)]        # 30只虫子
        self.predators = [Predator(config=config) for _ in range(6)]  # 6只捕食者
        self.foods = [Food(config) for _ in range(70)]              # 70个食物

        # 数据记录（用于观察进化效果）
        self.iq_history = []      # 虫子平均智商历史
        self.pop_history = []    # 虫子数量历史
        self.pred_history = []   # 捕食者数量历史
        self.frame = 0             # 运行帧数（时间）

        # 可调参数（调节生态平衡）
        self.speed_mult = 1.0       # 速度倍率
        self.food_rate = 0.16       # 食物生成概率
        self.reproduce_mult = 1.0   # 繁殖倍率

    # 世界更新一帧（核心逻辑循环）
    def update(self):
        self.frame += 1  # 时间前进

        # 随机生成新食物
        if random.random() < self.food_rate:
            self.foods.append(Food(self.config))

        # ========== 更新所有虫子 ==========
        new_bugs = []
        for bug in self.bugs:
            bug.think_and_move(self.foods, self.predators)  # 思考、移动
            bug.eat(self.foods)                             # 吃食物
            # 尝试繁殖
            if random.random() < self.reproduce_mult:
                baby = bug.reproduce()
                if baby:
                    new_bugs.append(baby)

        # ========== 更新所有捕食者 ==========
        new_preds = []
        for p in self.predators:
            p.think_and_move(self.bugs)  # 思考、追捕
            p.hunt(self.bugs)            # 猎杀虫子
            # 尝试繁殖
            if random.random() < self.reproduce_mult:
                baby = p.reproduce()
                if baby:
                    new_preds.append(baby)

        # 过滤掉死亡个体，并加入新出生的个体
        self.bugs = [b for b in self.bugs if not b.is_dead()] + new_bugs
        self.predators = [p for p in self.predators if not p.is_dead()] + new_preds

        # 每30帧记录一次数据
        if self.frame % 30 == 0:
            self.record()

    # 记录当前生态数据：数量、智商
    def record(self):
        b = len(self.bugs)
        p = len(self.predators)
        # 计算平均智商
        iq = sum(bb.iq for bb in self.bugs) / b if b > 0 else 0
        self.pop_history.append(b)
        self.pred_history.append(p)
        self.iq_history.append(iq)

    # ========== 保存最优个体的大脑 ==========
    def save_best(self):
        # 保存智商最高的虫子
        if self.bugs:
            best = max(self.bugs, key=lambda x: x.iq)
            best.save_brain("bugs/best_bug.pth")
        # 保存能量最高的捕食者
        if self.predators:
            best = max(self.predators, key=lambda x: x.energy)
            best.save_brain("predators/best_pred.pth")

    # ========== 加载历史最优大脑 ==========
    def load_best(self):
        try:
            if self.bugs:
                self.bugs[0].load_brain("bugs/best_bug.pth")
            if self.predators:
                self.predators[0].load_brain("predators/best_pred.pth")
            print("✅ 基因存档加载成功！")
        except:
            print("⚠️ 无存档")