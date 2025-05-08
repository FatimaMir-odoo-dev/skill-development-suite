# from odoo import models


class GoalLogicHelper:
    @staticmethod
    def calculate_progress(goal):
        if goal.goal_status != "complete":
            return 0.0

        full_goal_mark = GoalLogicHelper._calculate_full_goal_mark(goal)
        smart_bonus = GoalLogicHelper._smart_criteria_bonus(goal)
        reflection_bonus = GoalLogicHelper._lesson_bonus(goal)
        penalty = GoalLogicHelper._incomplete_result_penalty(goal)

        return max(0.0, full_goal_mark + smart_bonus + reflection_bonus - penalty)
    #
    @staticmethod
    def _calculate_full_goal_mark(goal):
        goal_index = GoalLogicHelper._get_goal_position_in_category(goal)
        base = 20
        return max(0, base - 2 * (goal_index - 1))

    @staticmethod
    def _smart_criteria_bonus(goal):
        fields = [
            goal.specific_goal,
            goal.measurable_goal,
            goal.achievable_goal,
            goal.relevant_goal,
            goal.timed_goal,
        ]
        return sum(1 for f in fields if f)  # max 5%

    @staticmethod
    def _lesson_bonus(goal):
        fields = [goal.lesson_id.lesson_worked, goal.lesson_id.lesson_change, goal.lesson_id.lesson_learned]
        return 5 if all(fields) else 0

    @staticmethod
    def _incomplete_result_penalty(goal):
        if not goal.result_ids:
            return 1  # -1% if no results
        done_count = sum(1 for r in goal.result_ids if r.is_done)
        return 0 if done_count >= 2 else 1  # -1% if less than 2 marked done

    @staticmethod
    def _get_goal_position_in_category(goal):
        same_category_goals = goal.search([("category", "=", goal.category)], order="id")
        return list(same_category_goals.ids).index(goal.id) + 1