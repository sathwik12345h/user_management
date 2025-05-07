import pytest
from unittest.mock import mock_open, patch
from app.utils.template_manager import TemplateManager

# Test the initialization of TemplateManager
def test_template_manager_initialization():
    tm = TemplateManager()
    assert tm.root_dir is not None
    assert tm.templates_dir.is_dir()  # Ensure templates_dir points to a valid directory

# Test _read_template method
@patch("builtins.open", mock_open(read_data="header content"))
def test_read_template():
    tm = TemplateManager()
    result = tm._read_template('header.md')
    assert result == "header content"
    # Check that the file open function was called with the correct file path
    open.assert_called_with(tm.templates_dir / 'header.md', 'r', encoding='utf-8')

# Test _apply_email_styles method
def test_apply_email_styles():
    tm = TemplateManager()
    html_content = "<p>This is a paragraph</p>"
    styled_html = tm._apply_email_styles(html_content)

    # Check if the styles are applied correctly
    assert 'style="font-size: 16px; color: #666666; margin: 10px 0; line-height: 1.6;"' in styled_html
    assert 'style="font-family: Arial, sans-serif; font-size: 16px; color: #333333; background-color: #ffffff; line-height: 1.5;"' in styled_html

# Test render_template method
@patch("app.utils.template_manager.TemplateManager._read_template")
@patch("app.utils.template_manager.markdown2.markdown")
def test_render_template(mock_markdown, mock_read_template):
    # Mock the template reading and markdown conversion
    mock_read_template.side_effect = ["header markdown", "footer markdown", "Hello, {name}!"]
    mock_markdown.return_value = "<html><body>Hello, John!</body></html>"

    tm = TemplateManager()

    # Test render_template with a given context
    result = tm.render_template("main_template", name="John")

    # Ensure templates are read in correct order and markdown is converted to HTML
    mock_read_template.assert_any_call('header.md')
    mock_read_template.assert_any_call('footer.md')
    mock_read_template.assert_any_call('main_template.md')

    # Check that styles were applied
    assert '<div style="font-family: Arial, sans-serif; font-size: 16px; color: #333333; background-color: #ffffff; line-height: 1.5;">' in result
    assert "<html><body>Hello, John!</body></html>" in result
    assert mock_markdown.called
    