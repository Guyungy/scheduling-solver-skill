# Scheduling Solver Skill

一个面向企业排班场景的智能求解 Skill。

核心方法：

- 先做排班容量与可行性检查
- 将“休息日”和“具体班次”拆成两个求解阶段
- 使用 MILP 求解组合，而不是让大模型直接猜班表
- 发现无解时量化缺口，并生成多个可执行妥协预案
- 业务规则与求解 Skill 分离，规则由独立记忆维护

## 文件结构

- `SKILL.md`：智能排班求解 Skill
- `references/VERIFIED_METHOD.md`：2026 年 9 月实际跑通方法与真实工具记录
- `examples/verified_case_2026_09.json`：已验证案例参数

## 已验证技术方案

实际跑通案例使用：

- Python
- NumPy
- SciPy `scipy.optimize.milp`
- SciPy sparse matrix
- HiGHS MILP solver

没有把具体客户业务规则写死在 Skill 内。具体规则应由独立的《智能排班规则》记忆提供。
