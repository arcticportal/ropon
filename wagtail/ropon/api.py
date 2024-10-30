from ninja import NinjaAPI
from home.models import HomePage
from . import schemas

api = NinjaAPI()


@api.get("/home", response=schemas.HomePageSchema)
def home(request):
    return HomePage.objects.first()
