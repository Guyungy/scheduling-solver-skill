from solver.cp_sat_solver import solve, EMPLOYEES


def test_verified_case_2026_09():
    status, schedule, summary = solve()
    assert status in ('OPTIMAL', 'FEASIBLE')
    assert len(schedule) == 30

    for row in schedule:
        assert len(row['day']) == 5
        assert len(row['middle']) == 1
        assert len(row['night']) == 3
        assert len(row['rest']) == 3

    rest_counts = sorted(v['rest'] for v in summary.values())
    assert rest_counts == [7] * 6 + [8] * 6

    for name in EMPLOYEES:
        assert 7 <= summary[name]['night'] <= 8

    # max consecutive work <= 6 and rest->night forbidden
    for name in EMPLOYEES:
        states = []
        for row in schedule:
            state = next(s for s in ('day','middle','night','rest') if name in row[s])
            states.append(state)
        streak = 0
        for s in states:
            streak = 0 if s == 'rest' else streak + 1
            assert streak <= 6
        for d in range(1, len(states)):
            assert not (states[d-1] == 'rest' and states[d] == 'night')
