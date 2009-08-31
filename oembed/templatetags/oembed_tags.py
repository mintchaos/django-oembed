from django import template
from django.template.defaultfilters import stringfilter
from oembed.core import replace

register = template.Library()

def oembed(input, args):
    if args:
        width, height = args.lower().split('x')
        if not width and height:
            raise template.TemplateSyntaxError("Oembed's optional WIDTHxHEIGH" \
                "T argument requires WIDTH and HEIGHT to be positive integers.")
    else:
        width, height = None, None
    return replace(input, max_width=width, max_height=height)
oembed.is_safe = True
oembed = stringfilter(oembed)

register.filter('oembed', oembed)

def do_oembed(parser, token):
    """
    A node which parses everything between its two nodes, and replaces any links
    with OEmbed-provided objects, if possible.
    
    Supports two optional argument, which is the maximum width and height, 
    specified like so:
    
        {% oembed 640x480 %}http://www.viddler.com/explore/SYSTM/videos/49/{% endoembed %}
    
    and or the name of a sub tempalte directory to render templates from:

        {% oembed 320x240 in "comments" %}http://www.viddler.com/explore/SYSTM/videos/49/{% endoembed %}
    
    or:
    
        {% oembed in "comments" %}http://www.viddler.com/explore/SYSTM/videos/49/{% endoembed %}
        
    either of those will render templates in oembed/comments/oembedtype.html
    """
    args = token.contents.split()
    if len(args) > 2:
        if len(args) == 3 and args[1] == "in":
            template_dir = args[2]
        elif len(args) == 4 and args[2] == "in":
            template_dir = args[3]
        else:
            raise template.TemplateSyntaxError("Oembed tag either takes a single (option" \
                "al) argument: WIDTHxHEIGHT, where WIDTH and HEIGHT are positive " \
                "integers, and or an optionan 'in \"template_dir\"' argument set.")
        if template_dir:
            if not (template_dir[0] == template_dir[-1] and template_dir[0] in ('"', "'")):
                raise template.TemplateSyntaxError("template_dir must be quoted")
            template_dir = template_dir[1:-1]
    else:
        template_dir = None
    if 'x' in args[1]:
        width, height = args[1].lower().split('x')
        if not width and height:
            raise template.TemplateSyntaxError("Oembed's optional WIDTHxHEIGH" \
                "T argument requires WIDTH and HEIGHT to be positive integers.")
    else:
        width, height = None, None
    nodelist = parser.parse(('endoembed',))
    parser.delete_first_token()
    return OEmbedNode(nodelist, width, height, template_dir)

register.tag('oembed', do_oembed)

class OEmbedNode(template.Node):
    def __init__(self, nodelist, width, height, template_dir):
        self.nodelist = nodelist
        self.width = width
        self.height = height
        self.template_dir = template_dir
    
    def render(self, context):
        kwargs = {}
        if self.width and self.height:
            kwargs['max_width'] = self.width
            kwargs['max_height'] = self.height
            kwargs['template_dir'] = self.template_dir
            kwargs['context'] = context
        return replace(self.nodelist.render(context), **kwargs)
