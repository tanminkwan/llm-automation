"""T-12: public API import 확인."""


class TestPublicAPI:
    """T-12: __init__ export 심볼 확인."""

    def test_all_exports(self) -> None:
        from celery_comment import (
            CommentResult,
            CommentSettings,
            FixtureGitClient,
            GitClient,
            SubprocessGitClient,
            TaskPayload,
            build_git_client,
            build_prompt,
            celery_app,
            create_celery_app,
            create_celery_task,
            process_comment,
        )

        assert all(
            [
                CommentResult,
                CommentSettings,
                FixtureGitClient,
                GitClient,
                SubprocessGitClient,
                TaskPayload,
                build_git_client,
                build_prompt,
                celery_app,
                create_celery_app,
                create_celery_task,
                process_comment,
            ]
        )
