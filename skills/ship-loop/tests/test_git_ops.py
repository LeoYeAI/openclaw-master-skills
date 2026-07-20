import pytest

from shiploop.git_ops import ALWAYS_BLOCKED, security_scan


class TestSecurityScan:
    def test_blocks_env_files(self):
        files = [".env", "src/main.py", ".env.local"]
        safe, blocked = security_scan(files)
        assert safe == ["src/main.py"]
        assert len(blocked) == 2

    def test_blocks_key_files(self):
        files = ["server.key", "cert.pem", "app.js"]
        safe, blocked = security_scan(files)
        assert safe == ["app.js"]
        assert len(blocked) == 2

    def test_blocks_credentials(self):
        files = ["credentials.json", "service-account-prod.json", "token.json", "config.json"]
        safe, blocked = security_scan(files)
        assert safe == ["config.json"]
        assert len(blocked) == 3

    def test_blocks_private_keys(self):
        files = ["id_rsa", "id_ed25519", "src/utils.py"]
        safe, blocked = security_scan(files)
        assert safe == ["src/utils.py"]
        assert len(blocked) == 2

    def test_blocks_node_modules(self):
        files = ["node_modules/lodash/index.js", "src/app.js"]
        safe, blocked = security_scan(files)
        assert safe == ["src/app.js"]
        assert len(blocked) == 1

    def test_blocks_pycache(self):
        files = ["__pycache__/main.cpython-311.pyc", "main.py"]
        safe, blocked = security_scan(files)
        assert safe == ["main.py"]
        assert len(blocked) == 1

    def test_blocks_learnings_yml(self):
        files = ["learnings.yml", "config.yml"]
        safe, blocked = security_scan(files)
        assert safe == ["config.yml"]
        assert len(blocked) == 1

    def test_extra_patterns(self):
        files = ["secret.txt", "readme.md", "deploy.sh"]
        safe, blocked = security_scan(files, extra_patterns=["secret.txt", "*.sh"])
        assert safe == ["readme.md"]
        assert len(blocked) == 2

    def test_all_safe(self):
        files = ["src/main.py", "src/utils.py", "README.md"]
        safe, blocked = security_scan(files)
        assert safe == files
        assert blocked == []

    def test_empty_input(self):
        safe, blocked = security_scan([])
        assert safe == []
        assert blocked == []

    def test_blocked_match_includes_pattern(self):
        files = [".env"]
        _, blocked = security_scan(files)
        assert len(blocked) == 1
        assert "(matched:" in blocked[0]
