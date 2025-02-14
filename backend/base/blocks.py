
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

class HeadingBlock(blocks.StructBlock):
    heading_text = blocks.CharBlock(required=True)
    heading_level = blocks.ChoiceBlock(choices=[
        ('h1', 'H1'),
        ('h2', 'H2'),
        ('h3', 'H3'),
        ('h4', 'H4'),
    ], default='h2')

    class Meta:
        icon = 'title'
        label = 'Heading'

class RoponImageChooserBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    caption = blocks.CharBlock(
        required=False,
        help_text="Add a caption to describe the image",
        # label="Caption"
    )
    attribution = blocks.CharBlock(
        required=False,
        help_text="Credit the image source or photographer",
        # label="Attribution"
    )
    class Meta:
        icon = 'image'
        label = 'Image'

    def get_api_representation(self, value, context=None):
        if value:
            image = value.get('image')
            return {
                'id': image.id,
                'title': image.title,
                'url': image.file.url,
                'width': image.width,
                'height': image.height,
                'caption': value.get('caption', ''),
                'attribution': value.get('attribution', '')
            }
        else:
            return None
        
class RoponRichTextBlock(blocks.RichTextBlock):
    
    def __init__(self, **kwargs):
        features = [
                    'bold', 'italic', 
                    'ol', 'ul', 'hr', 
                    'link', 
                ]
        super().__init__( features=features, **kwargs)
