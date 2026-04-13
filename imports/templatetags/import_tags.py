from django import template

register = template.Library()


@register.filter(name='get_section')
def get_section(report, key):
    """Get a section from the report dict by key."""
    if isinstance(report, dict):
        return report.get(key, {'create': [], 'update': [], 'skip': [], 'errors': []})
    return {'create': [], 'update': [], 'skip': [], 'errors': []}
