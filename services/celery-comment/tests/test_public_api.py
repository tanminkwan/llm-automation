"""T-12: public API import 확인."""


class TestPublicAPI:
    """T-12: __init__ export 심볼 확인."""

    def test_all_exports(self) -> None:
        from celery_comment import (
            AgentRunResult,
            CommentResult,
            CommentSettings,
            DirectLLMAgent,
            FixtureGitClient,
            GitClient,
            SubprocessGitClient,
            TaskPayload,
            build_agent_executor,
            build_git_client,
            build_prompt,
            build_worker_app,
            celery_app,
            create_celery_app,
            create_celery_task,
            process_comment,
        )

        assert all(
            [
                AgentRunResult,
                CommentResult,
                CommentSettings,
                DirectLLMAgent,
                FixtureGitClient,
                GitClient,
                SubprocessGitClient,
                TaskPayload,
                build_agent_executor,
                build_git_client,
                build_prompt,
                build_worker_app,
                celery_app,
                create_celery_app,
                create_celery_task,
                process_comment,
            ]
        )
