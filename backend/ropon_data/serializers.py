from rest_framework import serializers


# class NameOnlySerializer(serializers.ModelSerializer):
#     class Meta:
#         fields = ['name']

#     def __init__(self, *args, **kwargs):
#         model = kwargs.pop('model', None)
#         super().__init__(*args, **kwargs)
#         if model:
#             self.Meta.model = model