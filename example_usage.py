"""
Example usage of Temporal Plan Simple Temporal Network STN Skill.
"""

from client import SimpleTemporalNetwork


def main():
    print("=== Simple Temporal Network STN Demonstration ===")
    stn = SimpleTemporalNetwork()

    # Model multi-agent task execution deadlines:
    # 1. Task A starts after origin: [0, 5]
    # 2. Task A duration: [10, 15]
    # 3. Task B starts after Task A finishes: [2, 5]
    # 4. Task B duration: [5, 10]
    # 5. Global Deadline: Task B finish <= 40
    stn.add_constraint("origin", "task_A_start", min_duration=0, max_duration=5)
    stn.add_constraint("task_A_start", "task_A_end", min_duration=10, max_duration=15)
    stn.add_constraint("task_A_end", "task_B_start", min_duration=2, max_duration=5)
    stn.add_constraint("task_B_start", "task_B_end", min_duration=5, max_duration=10)
    stn.add_constraint("origin", "task_B_end", min_duration=0, max_duration=40)

    res = stn.solve()
    print("Is Schedule Temporally Consistent?", res["is_consistent"])
    print("\nComputed Earliest/Latest Temporal Schedule:")
    for node, bounds in res["schedule"].items():
        print(f"  {node:<15}: Earliest = {bounds['earliest_time']:>4.1f}s | Latest = {bounds['latest_time']:>4.1f}s | Slack = {bounds['slack']:>4.1f}s")


if __name__ == "__main__":
    main()
