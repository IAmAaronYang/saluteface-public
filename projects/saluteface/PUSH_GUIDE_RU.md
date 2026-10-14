# Git Bash: загрузка overlay в SchemaPilot

## 1. GitHub CLI выход и вход

```bash
gh auth logout -h github.com || true
gh auth login -h github.com -p https -w
gh auth status
```

## 2. Клонировать репозиторий и сохранить историю

```bash
cd /c/Users/Raws/Desktop
git clone https://github.com/bramrahanddian/SchemaPilot.git
cd SchemaPilot
git checkout -b feat/saluteface-research
```

Распакуйте архив `saluteface_overlay.zip` во временную папку рядом с `SchemaPilot`. **До копирования проверьте конфликты**: пакетный pyproject.toml и корневой README.md могут перезаписать существующие настройки SchemaPilot. Лучше переносить новые файлы в `projects/saluteface/`, оставляя существующий проект нетронутым:

```bash
mkdir -p projects/saluteface
cp -R ../saluteface_overlay/. projects/saluteface/
python -m pip install -e './projects/saluteface[dev]'
python -m pytest -q projects/saluteface/tests
git status --short
git add projects/saluteface
git commit -m "feat: add Saluteface reproducible sequence research toolkit"
git push -u origin feat/saluteface-research
```

Создайте PR из `feat/saluteface-research` в `main`. Это сохраняет всю исходную историю SchemaPilot и позволяет проверить изменение до слияния. Для `gh`:

```bash
gh pr create --base main --head feat/saluteface-research --title "Add Saluteface research toolkit" --body "Adds original sequence dataset tooling, toy watermark protocol, tests and CI without modifying SchemaPilot history."
```

## О bio/описании репозитория

Если у вашей учётной записи есть право администратора, описание репозитория корректнее обновить на `SchemaPilot and Saluteface research tools — reproducible structured-data contracts and protein-sequence research experiments`. Не заявляйте о правах на стороннее исследование и не удаляйте сведения об авторах SchemaPilot. `gh repo edit --description "..."` можно использовать только при наличии admin прав.

## О zauth

Никакой гарантированный score невозможен без опубликованной методики и реального запуска. Не создавайте искусственные коммиты, не подменяйте даты и не выдавайте перенесённые файлы за старую разработку Saluteface. Улучшайте подтверждаемые критерии: настоящие тесты, статический анализ, безопасность зависимостей, документацию, CI, лицензирование и воспроизводимость.

### CI при вложенной установке

Вложенная `.github/workflows` сама по себе не запускается. В корне SchemaPilot создайте `.github/workflows/saluteface-ci.yml` и перенесите туда workflow из ZIP, поправив команды на:

- `python -m pip install -e './projects/saluteface[dev]'`
- `python -m pytest -q projects/saluteface/tests`
- `python -m build projects/saluteface`
- `python -m compileall -q projects/saluteface/saluteface`

Добавьте корневой workflow через `git add .github/workflows/saluteface-ci.yml` до коммита. Не перезаписывайте существующие workflow проекта.
