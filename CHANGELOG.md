# Changelog

All notable changes to this repository will be documented in this file.

## [Unreleased] - 2026-09-12

- 新增 CURRENT_RESULTS.json、只读完整性校验与新旧成果逐项对应清单。
- 默认分析入口统一为 reproduce.py；旧 C01–C23 仅显式允许后执行，新 notebook 默认只读验证。
- 首页、依赖入口和协作说明统一到当前观察性分析；旧版本原文保存在 Archive/pre-unification-20260912。
- 历史 Word、图表、数据和运行产物未覆盖；正式论文另存方案待用户确认。
- 本次身份统一没有修复剩余统计审计问题，也没有重新发布软件版本。

## [1.5] - 2026-04-15

### Added

- Added repository governance files for public GitHub release: LICENSE, LICENSE_POLICY, CITATION, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, and issue/PR templates.
- Added requirements.txt for Python environment setup and notebook support.

### Changed

- Updated README with repository-facing usage, licensing, citation, and governance guidance.
- Expanded .gitignore to reduce accidental publication of local caches, temp files, and notebook artifacts.

### Notes

- Data licensing remains upstream-dependent and is not covered by the repository-wide code license.
