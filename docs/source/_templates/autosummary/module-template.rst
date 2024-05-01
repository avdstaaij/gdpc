{{ fullname | escape | underline}}

.. automodule:: {{ fullname }}
   :members:
   :undoc-members:

   {% block modules %}
   {% if modules %}
   .. rubric:: Modules

   .. autosummary::
      :toctree:
      :template: autosummary/module-template.rst
      :recursive:
   {% for item in modules %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}
