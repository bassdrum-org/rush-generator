# テスト関連ファイル削除計画

## 削除対象

### 1. ディレクトリ
- tests/ ディレクトリ全体
  - unit/テスト
  - integration/テスト
  - conftest.py
- .pytest_cache/ （存在する場合）
- coverage_html_report/ （存在する場合）

### 2. 設定ファイル
- pytest.ini

### 3. ドキュメント
- test_improvements.md
- test_structure_analysis.md

### 4. 依存関係の更新
requirements-dev.txtから以下を削除：
```
pytest>=8.3.4
pytest-cov>=6.0.0
```
※ `-r requirements.txt` の行は維持

### 5. .gitignore の更新
以下の行を削除：
```
.coverage
```

## 実装手順

1. まず、requirements-dev.txtを更新
2. .gitignoreから.coverageエントリを削除
3. 全てのテスト関連ファイルとディレクトリを削除
4. 最後に、不要になったキャッシュディレクトリを削除

## 注意事項
- 削除前に、重要なテストケースやロジックが他のファイルに依存していないことを確認
- srcディレクトリ内のソースコードは一切変更しない
- 削除後、プロジェクトが正常に動作することを確認

## 復元計画
必要に応じて後で参照できるように、削除前に以下の手順で情報を保存することを推奨：

1. testsディレクトリ全体のバックアップを作成
2. test_improvements.mdとtest_structure_analysis.mdのバックアップを作成
3. pytest.iniの設定内容のバックアップを作成

これにより、将来必要になった場合に、テスト環境を再構築することが可能になります。