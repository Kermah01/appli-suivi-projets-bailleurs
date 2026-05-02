import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()

from imports.template_generator import generate_template

template = generate_template()
with open('Template_Import_Projets_Bailleurs.xlsx', 'wb') as f:
    f.write(template.getvalue())

print('✅ Template Excel généré avec succès : Template_Import_Projets_Bailleurs.xlsx')
