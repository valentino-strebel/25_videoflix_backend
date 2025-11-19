"""
Custom RQ worker classes used for testing or environments where forking
is not desired. Provides a simplified worker that executes jobs in the
current process without applying the default death penalty mechanism.
"""

from rq import Worker


class BaseDeathPenalty:
    """
    No-op death penalty class used to bypass RQ's default timeout mechanism.
    Acts as a placeholder for environments that do not support forking.
    """

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self, *args, **kwargs):
        pass

    def __exit__(self, *args, **kwargs):
        pass


class SimpleWorker(Worker):
    """
    Worker subclass that avoids job execution via fork().
    Instead, it runs jobs in the same thread/process, making it suitable for
    testing or restricted environments.
    """

    death_penalty_class = BaseDeathPenalty

    def main_work_horse(self, *args, **kwargs):
        """
        Override the work horse method to disable standard job execution logic.

        Raises:
            NotImplementedError: Always raised to signal the method is inactive.
        """
        raise NotImplementedError("Test worker does not implement this method")

    def execute_job(self, *args, **kwargs):
        """
        Execute the job directly in the current process without forking.

        Args:
            *args: Arguments passed to job execution.
            **kwargs: Keyword arguments passed to job execution.

        Returns:
            Any: Result returned by the job's perform_job method.
        """
        return self.perform_job(*args, **kwargs)
