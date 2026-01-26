# from odoo import models

import logging

_logger = logging.getLogger(__name__)


class ProgressLogicHelper:
    @staticmethod
    def calculate_progress(goal):
        _logger.info("Calculating progress for Goal ID: %s", goal.id)

        if goal.goal_status != "complete":
            _logger.info("Goal status is not complete: %s", goal.goal_status)
            return 0.0

        full_goal_mark = ProgressLogicHelper._calculate_full_goal_mark(goal)
        smart_bonus = ProgressLogicHelper._smart_criteria_bonus(goal)
        reflection_bonus = ProgressLogicHelper._lesson_bonus(goal)
        penalty = ProgressLogicHelper._incomplete_result_penalty(goal)

        _logger.info("Full mark: %s, SMART bonus: %s, Reflection bonus: %s, Penalty: %s",
                     full_goal_mark, smart_bonus, reflection_bonus, penalty)

        final_score = max(0.0, full_goal_mark + smart_bonus + reflection_bonus - penalty)
        _logger.info("Final calculated progress: %s", final_score)
        return final_score

    #
    @staticmethod
    def _calculate_full_goal_mark(goal):
        goal_index = ProgressLogicHelper._get_goal_position_in_category(goal)
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
        for lesson in goal.lesson_id:
            if lesson.lesson_worked and lesson.lesson_change and lesson.lesson_learned:
                return 5  # Bonus applied if at least one complete reflection exists
        return 0

    @staticmethod
    def _incomplete_result_penalty(goal):
        if not goal.result_ids:
            return 1  # -1% if no results
        done_count = sum(1 for r in goal.result_ids if r.is_done)
        return 0 if done_count >= 2 else 1  # -1% if less than 2 marked done

    @staticmethod
    def _get_goal_position_in_category(goal):
        same_category_goals = goal.search([
            ("category", "=", goal.category),
            ("skill_id", "=", goal.skill_id.id),
            # ("learner_id", "=", goal.learner_id.id) #ADDED
        ], order="id")

        goal_ids = list(same_category_goals.ids)
        return goal_ids.index(goal.id) + 1 if goal.id in goal_ids else 1
