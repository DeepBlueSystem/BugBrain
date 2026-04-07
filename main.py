import pygame
import yaml
import matplotlib.pyplot as plt
import pygame_gui
from core.modles import Bug, Predator, World

# 配置
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 初始化
pygame.init()
screen = pygame.display.set_mode((900, 650))
pygame.display.set_caption("🐛 BugBrain · 最终完整版：AI 人工生命生态系统")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
font_big = pygame.font.SysFont(None, 40)

# GUI管理器
manager = pygame_gui.UIManager((900, 650))

# 面板
save_btn = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((680, 20), (180, 40)),
    text="💾 保存最优基因",
    manager=manager
)
load_btn = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((680, 70), (180, 40)),
    text="📂 加载基因存档",
    manager=manager
)

# 世界
world = World(config, Bug, Predator)
plt.ion()
fig, ax = plt.subplots(figsize=(5, 3))

# 主循环
running = True
while running:
    delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == save_btn:
                world.save_best()
                print("✅ 基因已保存！")
            if event.ui_element == load_btn:
                world.load_best()

        manager.process_events(event)

    manager.update(delta)
    screen.fill((20, 20, 35))

    # 运行世界
    for _ in range(int(world.speed_mult)):
        world.update()

    # 绘制
    for food in world.foods:
        pygame.draw.circle(screen, food.color, (int(food.x), int(food.y)), 3)
    for bug in world.bugs:
        bug.draw(screen)
    for pred in world.predators:
        pred.draw(screen)

    # 信息面板
    pygame.draw.rect(screen, (0, 0, 0), (10, 10, 620, 170))
    pop = len(world.bugs)
    pred_num = len(world.predators)
    food_num = len(world.foods)
    iq = sum(b.iq for b in world.bugs)/pop if pop>0 else 0
    gen = max((b.generation for b in world.bugs), default=0)

    screen.blit(font.render(f"🐛 虫子：{pop}", True, (180,220,80)), (20,20))
    screen.blit(font.render(f"🩸 捕食者：{pred_num}", True, (255,80,80)), (20,50))
    screen.blit(font.render(f"🍎 食物：{food_num}", True, (0,255,80)), (20,80))
    screen.blit(font.render(f"🧠 虫子智商：{iq:.2f}", True, (220,220,255)), (20,110))
    screen.blit(font.render(f"🧬 最高世代：{gen}", True, (255,200,150)), (20,140))

    screen.blit(font.render(f"▶ 速度：{world.speed_mult:.1f}x", True, (200,200,200)), (320,20))
    screen.blit(font.render(f"🍀 食物率：{world.food_rate:.2f}", True, (200,200,200)), (320,50))
    screen.blit(font.render(f"🐣 繁殖倍率：{world.reproduce_mult:.1f}x", True, (200,200,200)), (320,80))

    # 绘制GUI
    manager.draw_ui(screen)

    # 生态曲线
    if len(world.pop_history) > 2:
        ax.clear()
        ax.plot(world.pop_history, label="bugs", color=(0.7,1,0.3))
        ax.plot(world.pred_history, label="predators", color="red")
        ax.legend()
        ax.set_ylim(0)
        plt.pause(0.01)

    pygame.display.flip()

plt.ioff()
pygame.quit()