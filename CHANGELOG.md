# Changelog

All notable changes to this repository will be documented in this file.

## [Unreleased] - 2026-09-20

- 旧工程、缓存、图表、运行和 END 结项材料迁至 Legacy，保留最近的未提交修改；原始数据与论文工作稿保持原位。
- 当前工程整合为 Codes/C00–C06，恢复 Data、Reports、Tables、Pictures 分运行产出与 C/R/T/P 编号约定。
- 从七片原始数据完成整合试运行，13 项数据/统计产物与归档 final-v3 字节一致。
- 加入输出保护、依赖校验、输入/源码/产物哈希追踪、报告图形和当前入口测试；统计局限及论文修订仍待后续。

## [Previous working-tree changes] - 2026-09-12

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
