{{ fullname | escape | underline}}

.. automodule:: {{ fullname }}
   :members:
   :special-members:
   :undoc-members:
   :exclude-members: __str__, __repr__, __eq__, __weakref__, __subclasshook__, __annotations__, __dataclass_fields__, __dataclass_params__, __dict__, __module__, __abstractmethods__, __parameters__, __protocol_attrs__

   |

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

   |

   {% endif %}
   {% endblock %}
