# Template Creation Tutorial

This guide explains how to create a new manuscript template for the formatter pipeline.

## 1. Create Template Folder

Create a new folder in:

`backend/app/templates/<template_name>/`

Recommended files:

- `template.docx` (required)
- `contract.yaml` (recommended)
- `styles.csl` (optional, for CSL reference style)

Example:

`backend/app/templates/my_journal/template.docx`

## 2. Add Jinja2 Tags in DOCX

Open `template.docx` in Microsoft Word and add Jinja tags where content should render.

Use variables:

- `{{ title }}`
- `{{ abstract }}`
- `{{ page_number }}`

Use loops:

- `{% for author in authors %} ... {% endfor %}`
- `{% for section in sections %} ... {% endfor %}`
- `{% for reference in references %} ... {% endfor %}`

Use conditionals:

- `{% if cover_page %} ... {% endif %}`
- `{% if toc %} ... {% endif %}`
- `{% if page_numbers %} ... {% endif %}`

## 3. Minimal Template Snippets

### Title Block

```jinja
{{ title }}
{% for author in authors %}
{{ author }}
{% endfor %}
```

### Sections

```jinja
{% for section in sections %}
{{ section.heading }}
{% for paragraph in section.paragraphs %}
{{ paragraph }}
{% endfor %}
{% endfor %}
```

### References

```jinja
{% if references %}
References
{% for reference in references %}
{{ reference }}
{% endfor %}
{% endif %}
```

## 4. Screenshot Slots (Tutorial)

![Template DOCX with Jinja tags](./screenshots/10-template-docx-jinja.png)
![Rendered output sample](./screenshots/11-rendered-template-output.png)

## 5. Validate the Template

Run backend template tests:

```bash
cd backend
python -m pytest tests/test_template_renderer.py
```

Run CSL/template integration:

```bash
python -m pytest tests/integration/test_csl_formatting.py --no-cov
```

## 6. Template Quality Checklist

- No unresolved Jinja tags remain after rendering.
- Cover page appears only when enabled.
- TOC appears only when enabled.
- Page numbers appear only when enabled.
- References render correctly with selected citation style.

## 7. Rollout Steps

1. Add template folder and files.
2. Commit template assets.
3. Run tests.
4. Validate manually using one sample `.docx`, one `.pdf`, and one `.tex`.
5. Release.
