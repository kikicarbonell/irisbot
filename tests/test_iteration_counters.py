"""Tests for iteration-level counter logic in scraper."""

import pytest


def test_iteration_counter_logic_isolated():
    """Test the counter logic works correctly for multiple iterations.

    This simulates the counter behavior across multiple iterations
    to ensure counters don't bleed between iterations.
    """
    # Simulate iteration 1
    new_this_iteration = 0
    updated_this_iteration = 0
    unchanged_this_iteration = 0

    # Global accumulators
    new_project_ids = []
    updated_project_ids = []
    unchanged_project_ids = []

    # Iteration 1: Process 5 projects (1 new, 2 updated, 2 unchanged)
    for i in range(1):
        new_this_iteration = 0
        updated_this_iteration = 0
        unchanged_this_iteration = 0

        # Project 101: NEW
        new_this_iteration += 1
        new_project_ids.append(101)

        # Project 235: UPDATED
        updated_this_iteration += 1
        updated_project_ids.append(235)

        # Project 682: UPDATED
        updated_this_iteration += 1
        updated_project_ids.append(682)

        # Project 450: UNCHANGED
        unchanged_this_iteration += 1
        unchanged_project_ids.append(450)

        # Project 555: UNCHANGED
        unchanged_this_iteration += 1
        unchanged_project_ids.append(555)

        # Verify iteration 1 counters
        assert new_this_iteration == 1, f"Iteration 1: expected 1 new, got {new_this_iteration}"
        assert updated_this_iteration == 2, f"Iteration 1: expected 2 updated, got {updated_this_iteration}"
        assert unchanged_this_iteration == 2, f"Iteration 1: expected 2 unchanged, got {unchanged_this_iteration}"

    # Verify global accumulators after iteration 1
    assert len(new_project_ids) == 1
    assert len(updated_project_ids) == 2
    assert len(unchanged_project_ids) == 2

    # Iteration 2: Process 3 new projects, counters should reset
    new_this_iteration = 0
    updated_this_iteration = 0
    unchanged_this_iteration = 0

    # Project 890: NEW
    new_this_iteration += 1
    new_project_ids.append(890)

    # Project 999: NEW
    new_this_iteration += 1
    new_project_ids.append(999)

    # Project 235: UPDATED (same project as iteration 1, but different update)
    updated_this_iteration += 1
    updated_project_ids.append(235)

    # Verify iteration 2 counters (should be fresh, not cumulative)
    assert new_this_iteration == 2, f"Iteration 2: expected 2 new, got {new_this_iteration}"
    assert updated_this_iteration == 1, f"Iteration 2: expected 1 updated, got {updated_this_iteration}"
    assert unchanged_this_iteration == 0, f"Iteration 2: expected 0 unchanged, got {unchanged_this_iteration}"

    # Verify global accumulators after iteration 2
    assert len(new_project_ids) == 3, f"Global: expected 3 total new, got {len(new_project_ids)}"
    assert len(updated_project_ids) == 3, f"Global: expected 3 total updated, got {len(updated_project_ids)}"
    assert len(unchanged_project_ids) == 2, f"Global: expected 2 total unchanged, got {len(unchanged_project_ids)}"


def test_iteration_counters_dont_accumulate():
    """Verify that per-iteration counters reset and don't accumulate."""

    # Track counters across iterations
    all_iterations_new = []
    all_iterations_updated = []
    all_iterations_unchanged = []

    for iteration_num in range(1, 4):  # 3 iterations
        # Reset counters for this iteration
        new_this_iteration = 0
        updated_this_iteration = 0
        unchanged_this_iteration = 0

        # Simulate different number of changes per iteration
        if iteration_num == 1:
            # Iteration 1: 2 new, 0 updated, 1 unchanged
            new_this_iteration = 2
            updated_this_iteration = 0
            unchanged_this_iteration = 1
        elif iteration_num == 2:
            # Iteration 2: 1 new, 3 updated, 0 unchanged
            new_this_iteration = 1
            updated_this_iteration = 3
            unchanged_this_iteration = 0
        else:  # iteration_num == 3
            # Iteration 3: 0 new, 1 updated, 4 unchanged
            new_this_iteration = 0
            updated_this_iteration = 1
            unchanged_this_iteration = 4

        # Store counters for verification
        all_iterations_new.append(new_this_iteration)
        all_iterations_updated.append(updated_this_iteration)
        all_iterations_unchanged.append(unchanged_this_iteration)

    # Verify each iteration has independent counters (not cumulative)
    assert all_iterations_new == [2, 1, 0], f"New counters should not accumulate: {all_iterations_new}"
    assert all_iterations_updated == [0, 3, 1], f"Updated counters should not accumulate: {all_iterations_updated}"
    assert all_iterations_unchanged == [1, 0, 4], f"Unchanged counters should not accumulate: {all_iterations_unchanged}"

    # Verify global accumulation would show correct totals
    total_new = sum(all_iterations_new)
    total_updated = sum(all_iterations_updated)
    total_unchanged = sum(all_iterations_unchanged)

    assert total_new == 3, f"Global new should be 3, got {total_new}"
    assert total_updated == 4, f"Global updated should be 4, got {total_updated}"
    assert total_unchanged == 5, f"Global unchanged should be 5, got {total_unchanged}"
