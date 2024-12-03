
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

class HeadingBlock(blocks.StructBlock):
    heading_text = blocks.CharBlock(required=True)
    header_level = blocks.ChoiceBlock(choices=[
        ('h1', 'H1'),
        ('h2', 'H2'),
        ('h3', 'H3'),
        ('h4', 'H4'),
    ], default='h2')

    class Meta:
        icon = 'title'
        label = 'Heading'

class RoponImageChooserBlock(ImageChooserBlock):
    def get_api_representation(self, value, context=None):
        if value:
            return {
                'id': value.id,
                'title': value.title,
                'url': value.file.url,
                'width': value.width,
                'height': value.height,
            }
        else:
            return None
        
class RoponRichTextBlock(blocks.RichTextBlock):
    
    def __init__(self, **kwargs):
        features = ['h2', 'h3', 'h4',
                    'bold', 'italic', 
                    'ol', 'ul', 'hr', 
                    'link', 
                ]
        super().__init__( features=features, **kwargs)
