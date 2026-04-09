from typing import Any

from src.modules.admin.repositories.admin_user_repository import AdminUserRepository


class AdminAuthService:
    def __init__(
        self,
        repo: AdminUserRepository | None = None,
        default_admin_ids_str: str | None = None,
    ):
        self.repo = repo or AdminUserRepository()
        self.default_admin_ids = self._parse_default_admin_ids(default_admin_ids_str)

    @staticmethod
    def _parse_default_admin_ids(raw: str | None) -> set[str]:
        if not raw:
            return set()
        return {part.strip() for part in str(raw).split(',') if part.strip()}

    def init_and_sync(self) -> None:
        self.repo.init_table()
        self.sync_default_admins()

    def sync_default_admins(self) -> None:
        for user_id in self.default_admin_ids:
            self.repo.upsert_admin(user_id=user_id, username=None)

    def is_default_admin(self, user_id: str | int) -> bool:
        return str(user_id).strip() in self.default_admin_ids

    def is_admin(self, user_id: str | int) -> bool:
        user_id = str(user_id).strip()
        if self.is_default_admin(user_id):
            return True
        row = self.repo.get_user_by_id(user_id)
        if not row:
            return False
        return (
            str(row.get('role', '')).upper() == 'ADMIN'
            and int(row.get('is_active', 0)) == 1
        )

    def add_admin(self, user_id: str | int, username: str | None = None) -> None:
        self.repo.upsert_admin(user_id=str(user_id).strip(), username=username)

    def remove_admin(self, user_id: str | int) -> tuple[bool, str]:
        user_id = str(user_id).strip()
        if self.is_default_admin(user_id):
            return False, '❌ This admin is protected by DEFAULT_ADMIN_USER_IDS'
        row = self.repo.get_user_by_id(user_id)
        if not row:
            return False, '❌ User not found in admin database'
        self.repo.demote_to_user(user_id)
        return True, f'✅ Admin removed\nUser ID: {user_id}'

    def list_admins(self) -> list[dict[str, Any]]:
        rows = self.repo.list_active_admins()
        result = []
        for row in rows:
            user_id = str(row.get('user_id', '')).strip()
            result.append(
                {
                    'user_id': user_id,
                    'username': row.get('username'),
                    'role': 'ADMIN',
                    'is_default': self.is_default_admin(user_id),
                }
            )
        existing_ids = {item['user_id'] for item in result}
        for user_id in sorted(self.default_admin_ids):
            if user_id not in existing_ids:
                result.append(
                    {
                        'user_id': user_id,
                        'username': None,
                        'role': 'ADMIN',
                        'is_default': True,
                    }
                )
        result.sort(key=lambda x: x['user_id'])
        return result
