from __future__ import annotations

from .github_parser import parse_github_log as parse_github_log
from .jenkins_parser import parse_jenkins_log as parse_jenkins_log

__all__ = ["parse_github_log", "parse_jenkins_log"]
