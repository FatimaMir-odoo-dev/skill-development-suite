"""
Count mixin utilities.

Provides a reusable abstract model with helper logic to compute counts
of related records using efficient grouped queries.
"""

from odoo import api, fields, models  # noqa: F401


class CountMixin(models.AbstractModel):
    """Abstract mixin providing generic count computation utilities."""
    _name = 'count.mixin'
    _description = 'Count Mixin'

    def _compute_count(self, count_field, counted_model, related_field):
        """
                Generic method to count related records.

                :param count_field: str - name of the computed field to update (e.g., 'task_count')
                :param counted_model: str - model name of the related records to be counted
                    (e.g., 'skill_development.task')
                :param related_field: str - field name on related model that links back (e.g., 'goal_id') NAH BETTER DESC # noqa: E501
                """

        # Early return if no records to process
        if not self:
            return

        # Use read_group to count fields in a single query
        field_counts = self.env[counted_model].read_group(
            domain=[(related_field, 'in', self.ids)],
            fields=[related_field],
            groupby=[related_field]
        )

        # Build a simple lookup dictionary: goal_id -> count
        counts_by_id = {}
        for item in field_counts:
            record_id = item[related_field][0]  # read_group returns (id, name) tuple
            count = item[f'{related_field}_count']
            counts_by_id[record_id] = count

        # Assign counts to each record
        for record in self:
            setattr(record, count_field, counts_by_id.get(record.id, 0))
