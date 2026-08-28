from ortools.sat.python import cp_model

EMPLOYEES = [
    '伍微芬','向宇琼','张可','李雨彤','陈洁','张丽丽',
    '王俪桦','张佳佳','杨镇肇','黄紫娟','郭于扬','雷巧玲'
]
DAYS = 30
SHIFTS = ['day', 'middle', 'night', 'rest']
TARGET = {'day': 5, 'middle': 1, 'night': 3, 'rest': 3}


def solve():
    model = cp_model.CpModel()
    x = {(e,d,s): model.new_bool_var(f'x_{e}_{d}_{s}')
         for e in range(len(EMPLOYEES)) for d in range(DAYS) for s in SHIFTS}

    # 每人每天恰好一个状态
    for e in range(len(EMPLOYEES)):
        for d in range(DAYS):
            model.add_exactly_one(x[e,d,s] for s in SHIFTS)

    # 每日固定 5早 + 1中 + 3晚 + 3休
    for d in range(DAYS):
        for s, count in TARGET.items():
            model.add(sum(x[e,d,s] for e in range(len(EMPLOYEES))) == count)

    # 容量妥协：6人休8天，6人休7天
    for e in range(len(EMPLOYEES)):
        rest_target = 8 if e < 6 else 7
        model.add(sum(x[e,d,'rest'] for d in range(DAYS)) == rest_target)

    # 晚班公平：每人7~8天
    for e in range(len(EMPLOYEES)):
        nights = sum(x[e,d,'night'] for d in range(DAYS))
        model.add(nights >= 7)
        model.add(nights <= 8)

    # 连续工作最多6天：任意7天至少休1天
    for e in range(len(EMPLOYEES)):
        for start in range(DAYS - 6):
            model.add(sum(x[e,d,'rest'] for d in range(start, start + 7)) >= 1)

    # 禁止 休 -> 晚
    for e in range(len(EMPLOYEES)):
        for d in range(1, DAYS):
            model.add(x[e,d-1,'rest'] + x[e,d,'night'] <= 1)

    # 避免孤立晚班，至少与前后一天中的一个晚班相邻
    for e in range(len(EMPLOYEES)):
        model.add(x[e,0,'night'] <= x[e,1,'night'])
        model.add(x[e,DAYS-1,'night'] <= x[e,DAYS-2,'night'])
        for d in range(1, DAYS-1):
            model.add(x[e,d,'night'] <= x[e,d-1,'night'] + x[e,d+1,'night'])

    # 避免孤立单休
    for e in range(len(EMPLOYEES)):
        for d in range(1, DAYS-1):
            model.add(x[e,d,'rest'] <= x[e,d-1,'rest'] + x[e,d+1,'rest'])

    # 软目标：中班尽量均衡
    middle_counts = []
    for e in range(len(EMPLOYEES)):
        c = model.new_int_var(0, DAYS, f'middle_count_{e}')
        model.add(c == sum(x[e,d,'middle'] for d in range(DAYS)))
        middle_counts.append(c)
    max_mid = model.new_int_var(0, DAYS, 'max_mid')
    min_mid = model.new_int_var(0, DAYS, 'min_mid')
    model.add_max_equality(max_mid, middle_counts)
    model.add_min_equality(min_mid, middle_counts)
    model.minimize(max_mid - min_mid)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30
    solver.parameters.num_search_workers = 8
    status = solver.solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError(f'CP-SAT failed: {solver.status_name(status)}')

    schedule = []
    for d in range(DAYS):
        row = {'day': [], 'middle': [], 'night': [], 'rest': []}
        for e, name in enumerate(EMPLOYEES):
            for s in SHIFTS:
                if solver.value(x[e,d,s]):
                    row[s].append(name)
        schedule.append(row)

    summary = {}
    for e, name in enumerate(EMPLOYEES):
        summary[name] = {s: sum(solver.value(x[e,d,s]) for d in range(DAYS)) for s in SHIFTS}

    return solver.status_name(status), schedule, summary


if __name__ == '__main__':
    status, schedule, summary = solve()
    print('STATUS:', status)
    for name, counts in summary.items():
        print(name, counts)
